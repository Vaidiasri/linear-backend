import asyncio
import sys
import os

# Add the parent directory to sys.path to resolve 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.lib.database import AsyncSessionLocal
from app.services.user import UserService
from app.schemas.user import UserCreate
from app.model.user import UserRole
from app import crud


async def create_manager():
    async with AsyncSessionLocal() as session:
        email = "manager@example.com"
        password = "password123"
        full_name = "Manager User"

        # Check if user exists
        existing_user = await crud.user.get_by_email(session, email=email)
        if existing_user:
            print(f"User {email} already exists.")
            # Update role to TEAM_LEAD if not already
            if existing_user.role != UserRole.TEAM_LEAD:
                print(f"Updating role for {email} to TEAM_LEAD...")
                existing_user.role = UserRole.TEAM_LEAD
                session.add(existing_user)
                await session.commit()
                print("Role updated successfully!")
            else:
                print(f"User {email} is already a TEAM_LEAD.")
            return

        print(f"Creating new manager user: {email}")
        user_in = UserCreate(email=email, password=password, full_name=full_name)

        # We use UserService.create but we need to intercept to set the role,
        # as UserCreate doesn't have 'role' field (likely defaults to MEMBER).
        # Or we can use UserService.create then update.

        new_user = await UserService.create(session, user_in=user_in)

        # Now promote to TEAM_LEAD
        new_user.role = UserRole.TEAM_LEAD
        session.add(new_user)
        await session.commit()

        print("Manager user created successfully!")
        print(f"Email: {email}")
        print(f"Password: {password}")


if __name__ == "__main__":
    asyncio.run(create_manager())
