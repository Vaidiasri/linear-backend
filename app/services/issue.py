from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import csv
import io
from fastapi.responses import StreamingResponse

from app import model, crud
from app.schemas.issue import IssueCreate, IssueCreate as IssueUpdate
from app.filters import IssueFilters


class IssueService:
    @staticmethod
    async def validate_issue_entities(
        db: AsyncSession,
        project_id: Optional[UUID] = None,
        assignee_id: Optional[UUID] = None,
        team_id: Optional[UUID] = None,
    ):
        if project_id:
            project = await db.get(model.Project, project_id)
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
                )

        if assignee_id:
            assignee = await db.get(model.User, assignee_id)
            if not assignee:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Assignee user not found",
                )

        if team_id:
            team = await db.get(model.Team, team_id)
            if not team:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
                )

    @staticmethod
    async def create(
        db: AsyncSession, *, issue_in: IssueCreate, current_user: model.User
    ) -> model.Issue:
        # 1. Validate entities
        await IssueService.validate_issue_entities(
            db,
            project_id=issue_in.project_id,
            assignee_id=issue_in.assignee_id,
            team_id=issue_in.team_id,
        )

        # 2. Create Issue (using CRUD)
        # Note: We need to handle 'creator_id' manually since it's not in IssueCreate schema
        # but CRUDBase expects schema. We'll add it to the model constructor args manually in CRUD?
        # Actually CRUDBase uses jsonable_encoder(obj_in).
        # We can modify the dict before passing or handle it here.
        # Let's use the CRUD methodology but we need to inject creator_id.

        # Easier: Manually create object here or override create in CRUD.
        # Let's override create in CRUD? No, base create is generic.
        # Let's use lower-level model creation here or update schema data.

        db_obj = model.Issue(**issue_in.model_dump(), creator_id=current_user.id)
        db.add(db_obj)

        # 3. Activity Log
        creation_log = model.Activity(
            issue_id=db_obj.id,
            user_id=current_user.id,
            attribute="created",
            old_value="",
            new_value=f"Issue created by {current_user.email}",
        )
        db.add(creation_log)

        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def get_all(
        db: AsyncSession,
        *,
        filters: IssueFilters,
        skip: int = 0,
        limit: int = 10,
        current_user: model.User,
    ) -> List[model.Issue]:
        return await crud.issue.get_multi_by_owner(
            db,
            creator_id=current_user.id,
            skip=skip,
            limit=limit,
            status=filters.status,
            priority=filters.priority,
            team_id=filters.team_id,
            project_id=filters.project_id,
            assignee_id=filters.assignee_id,
            search=filters.search,
        )

    @staticmethod
    async def get(
        db: AsyncSession, *, id: UUID, current_user: model.User
    ) -> model.Issue:
        # get with relations
        issue = await crud.issue.get_with_relations(
            db, id=id, creator_id=current_user.id
        )
        if not issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Issue not found or you don't have access",
            )
        return issue

    @staticmethod
    async def update(
        db: AsyncSession,
        *,
        id: UUID,
        issue_in: IssueUpdate,
        current_user: model.User,
    ) -> model.Issue:
        # 1. Get existing issue
        issue = await crud.issue.get(db, id)
        if not issue or issue.creator_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Issue not found or you are not the owner",
            )

        # 2. Validate entities if changed
        await IssueService.validate_issue_entities(
            db,
            project_id=(
                issue_in.project_id if issue_in.project_id != issue.project_id else None
            ),
            assignee_id=(
                issue_in.assignee_id
                if issue_in.assignee_id != issue.assignee_id
                else None
            ),
            team_id=issue_in.team_id if issue_in.team_id != issue.team_id else None,
        )

        # 3. Track changes for activity log
        tracked_fields = ["status", "priority", "title", "assignee_id"]
        update_data = issue_in.model_dump(exclude_unset=True)

        for key, new_value in update_data.items():
            old_value = getattr(issue, key)
            if old_value != new_value:
                if key in tracked_fields:
                    new_log = model.Activity(
                        issue_id=issue.id,
                        user_id=current_user.id,
                        attribute=key,
                        old_value=str(old_value) if old_value is not None else "None",
                        new_value=str(new_value) if new_value is not None else "None",
                    )
                    db.add(new_log)
                setattr(issue, key, new_value)

        await db.commit()
        await db.refresh(issue)
        return issue

    @staticmethod
    async def delete(db: AsyncSession, *, id: UUID, current_user: model.User) -> None:
        issue = await crud.issue.get(db, id)
        if not issue or issue.creator_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Issue not found or you are not the owner",
            )
        await crud.issue.remove(db, id=id)

    @staticmethod
    async def search(
        db: AsyncSession, *, q: str, skip: int, limit: int
    ) -> List[model.Issue]:
        return await crud.issue.search_global(db, q=q, skip=skip, limit=limit)

    @staticmethod
    async def get_stats(db: AsyncSession, *, current_user: model.User) -> dict:
        return await crud.issue.get_stats(db, creator_id=current_user.id)

    @staticmethod
    async def export_csv(
        db: AsyncSession, *, filters: IssueFilters, current_user: model.User
    ) -> StreamingResponse:
        issues = await crud.issue.get_all_for_export(
            db,
            creator_id=current_user.id,
            status=filters.status,
            priority=filters.priority,
            team_id=filters.team_id,
            project_id=filters.project_id,
            assignee_id=filters.assignee_id,
            search=filters.search,
        )

        # Generator for StreamingResponse
        def iter_csv():
            output = io.StringIO()
            writer = csv.writer(output)
            # Header
            writer.writerow(
                [
                    "ID",
                    "Title",
                    "Status",
                    "Priority",
                    "Assignee",
                    "Project",
                    "Team",
                    "Created At",
                ]
            )
            yield output.getvalue()
            output.seek(0)
            output.truncate(0)

            for issue in issues:
                writer.writerow(
                    [
                        issue.identifier,
                        issue.title,
                        issue.status,
                        issue.priority,
                        issue.assignee.email if issue.assignee else "Unassigned",
                        issue.project.name if issue.project else "No Project",
                        issue.team.name if issue.team else "No Team",
                        issue.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    ]
                )
                yield output.getvalue()
                output.seek(0)
                output.truncate(0)

        return StreamingResponse(
            iter_csv(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=issues_report.csv"},
        )
