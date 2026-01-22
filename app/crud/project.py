from app.crud.base import CRUDBase
from app.model.project import Project
from app.schemas.project import ProjectCreate, ProjectCreate as ProjectUpdate


class CRUDProject(CRUDBase[Project, ProjectCreate, ProjectUpdate]):
    pass


project = CRUDProject(Project)
