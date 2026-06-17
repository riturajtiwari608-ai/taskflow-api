from fastapi import FastAPI

from app.database import Base, engine
from app.models import User, Workspace, Project, Task

from app.routes.auth_routes import router as auth_router
from app.routes.workspace_routes import router as workspace_router
from app.routes.project_routes import router as project_router
from app.routes.task_routes import router as task_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TaskFlow API",
    description="A team task management backend inspired by Jira and Trello",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "Welcome to TaskFlow API",
        "docs": "/docs"
    }


app.include_router(auth_router)
app.include_router(workspace_router)
app.include_router(project_router)
app.include_router(task_router)
app.include_router(comment_router)