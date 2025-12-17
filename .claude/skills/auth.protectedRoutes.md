---
description: Protected route patterns for FastAPI with Better Auth JWT verification
---

## Better Auth: Protected Routes (FastAPI)

This skill covers patterns for protecting FastAPI routes with Better Auth JWT verification.

### Prerequisites

- FastAPI application
- JWT verification configured (see `auth.jwt.verify` skill)
- Database session dependency

### Basic Protected Route

```python
from fastapi import APIRouter, Depends, HTTPException
from app.auth import User, get_current_user

router = APIRouter(prefix="/api", tags=["protected"])


@router.get("/me")
async def get_current_user_info(user: User = Depends(get_current_user)):
    """Get current user information from JWT."""
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
    }
```

### Resource Ownership Pattern

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.models import Task
from app.auth import User, get_current_user

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("/{task_id}")
async def get_task(
    task_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get a task - only if owned by current user."""
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Ownership check
    if task.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Delete a task - only if owned by current user."""
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    session.delete(task)
    session.commit()
```

### Ownership Helper Dependency

```python
from typing import TypeVar, Type
from sqlmodel import SQLModel

T = TypeVar("T", bound=SQLModel)


def get_owned_resource(model: Type[T], id_param: str = "id"):
    """
    Factory for ownership-checking dependencies.

    Usage:
        @router.get("/{task_id}")
        async def get_task(task: Task = Depends(get_owned_resource(Task, "task_id"))):
            return task
    """
    async def dependency(
        user: User = Depends(get_current_user),
        session: Session = Depends(get_session),
        **kwargs,
    ) -> T:
        resource_id = kwargs.get(id_param)
        resource = session.get(model, resource_id)

        if not resource:
            raise HTTPException(
                status_code=404,
                detail=f"{model.__name__} not found"
            )

        if hasattr(resource, "user_id") and resource.user_id != user.id:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to access this resource"
            )

        return resource

    return dependency
```

### List with Filtering

```python
from typing import Optional


@router.get("", response_model=list[TaskRead])
async def get_tasks(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    completed: Optional[bool] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
):
    """Get all tasks for the current user with optional filtering."""
    statement = select(Task).where(Task.user_id == user.id)

    # Apply filters
    if completed is not None:
        statement = statement.where(Task.completed == completed)

    if priority:
        statement = statement.where(Task.priority == priority)

    if search:
        statement = statement.where(Task.title.ilike(f"%{search}%"))

    # Pagination
    statement = statement.offset(skip).limit(min(limit, 100))

    # Order by created_at desc
    statement = statement.order_by(Task.created_at.desc())

    return session.exec(statement).all()
```

### Create Resource

```python
from datetime import datetime
from app.models import TaskCreate, TaskRead


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Create a new task for the current user."""
    task = Task(
        **task_data.model_dump(),
        user_id=user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
```

### Update Resource

```python
from app.models import TaskUpdate


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Update a task - only if owned by current user."""
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Only update provided fields
    update_data = task_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.put("/{task_id}", response_model=TaskRead)
async def replace_task(
    task_id: int,
    task_data: TaskCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Replace a task completely - only if owned by current user."""
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Replace all fields
    for key, value in task_data.model_dump().items():
        setattr(task, key, value)

    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
```

### Optional Authentication

```python
from typing import Optional
from fastapi import Header


async def get_optional_user(
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> Optional[User]:
    """Get user if authenticated, None otherwise."""
    if not authorization:
        return None

    try:
        from app.auth import verify_token
        return await verify_token(authorization)
    except HTTPException:
        return None


@router.get("/public")
async def public_endpoint(user: Optional[User] = Depends(get_optional_user)):
    """Endpoint accessible to both authenticated and anonymous users."""
    if user:
        return {"message": f"Hello, {user.name}!", "authenticated": True}
    return {"message": "Hello, guest!", "authenticated": False}


@router.get("/posts")
async def get_posts(
    user: Optional[User] = Depends(get_optional_user),
    session: Session = Depends(get_session),
):
    """Get posts - personalized for authenticated users."""
    if user:
        # Return personalized feed
        statement = select(Post).where(
            (Post.is_public == True) | (Post.user_id == user.id)
        )
    else:
        # Return public posts only
        statement = select(Post).where(Post.is_public == True)

    return session.exec(statement).all()
```

### Role-Based Access

```python
from typing import List


def require_role(*required_roles: str):
    """Dependency factory for role-based access."""
    async def role_checker(user: User = Depends(get_current_user)) -> User:
        if not hasattr(user, "role") or user.role not in required_roles:
            raise HTTPException(
                status_code=403,
                detail=f"One of roles {required_roles} required"
            )
        return user
    return role_checker


def require_any_role(*roles: str):
    """Require user to have any of the specified roles."""
    return require_role(*roles)


def require_admin():
    """Shortcut for admin-only routes."""
    return require_role("admin")


# Usage
@router.get("/admin/users")
async def list_all_users(
    user: User = Depends(require_role("admin")),
    session: Session = Depends(get_session),
):
    """Admin-only endpoint to list all users."""
    return session.exec(select(User)).all()


@router.get("/moderator/reports")
async def view_reports(
    user: User = Depends(require_any_role("admin", "moderator")),
    session: Session = Depends(get_session),
):
    """Admin or moderator can view reports."""
    return session.exec(select(Report)).all()
```

### Permission-Based Access

```python
def require_permission(*required_permissions: str):
    """Dependency factory for permission-based access."""
    async def permission_checker(user: User = Depends(get_current_user)) -> User:
        user_permissions = getattr(user, "permissions", []) or []
        missing = set(required_permissions) - set(user_permissions)

        if missing:
            raise HTTPException(
                status_code=403,
                detail=f"Missing permissions: {list(missing)}"
            )
        return user
    return permission_checker


# Usage
@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    user: User = Depends(require_permission("tasks:delete")),
    session: Session = Depends(get_session),
):
    """Requires tasks:delete permission."""
    task = session.get(Task, task_id)
    if task:
        session.delete(task)
        session.commit()
    return {"deleted": True}


@router.post("/bulk-import")
async def bulk_import(
    data: list[TaskCreate],
    user: User = Depends(require_permission("tasks:create", "tasks:bulk")),
    session: Session = Depends(get_session),
):
    """Requires both tasks:create and tasks:bulk permissions."""
    pass
```

### Bulk Operations

```python
@router.post("/bulk", response_model=list[TaskRead], status_code=201)
async def create_tasks_bulk(
    tasks_data: list[TaskCreate],
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Create multiple tasks at once."""
    now = datetime.utcnow()
    tasks = [
        Task(
            **data.model_dump(),
            user_id=user.id,
            created_at=now,
            updated_at=now,
        )
        for data in tasks_data
    ]
    session.add_all(tasks)
    session.commit()

    for task in tasks:
        session.refresh(task)

    return tasks


@router.delete("/bulk")
async def delete_completed_tasks(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Delete all completed tasks for the current user."""
    statement = select(Task).where(
        Task.user_id == user.id,
        Task.completed == True
    )
    tasks = session.exec(statement).all()

    for task in tasks:
        session.delete(task)

    session.commit()
    return {"deleted": len(tasks)}


@router.patch("/bulk/complete")
async def complete_all_tasks(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Mark all tasks as complete for the current user."""
    statement = select(Task).where(
        Task.user_id == user.id,
        Task.completed == False
    )
    tasks = session.exec(statement).all()

    for task in tasks:
        task.completed = True
        task.updated_at = datetime.utcnow()

    session.commit()
    return {"completed": len(tasks)}
```

### Pagination Response Pattern

```python
from pydantic import BaseModel
from typing import Generic, TypeVar, List

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int


@router.get("/paginated", response_model=PaginatedResponse[TaskRead])
async def get_tasks_paginated(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    page: int = 1,
    page_size: int = 20,
):
    """Get tasks with pagination metadata."""
    # Count total
    count_statement = select(func.count()).where(Task.user_id == user.id)
    total = session.exec(count_statement).one()

    # Fetch page
    offset = (page - 1) * page_size
    statement = (
        select(Task)
        .where(Task.user_id == user.id)
        .offset(offset)
        .limit(page_size)
        .order_by(Task.created_at.desc())
    )
    items = session.exec(statement).all()

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )
```

### Router-Level Protection

```python
from fastapi import APIRouter, Depends

# All routes in this router require authentication
protected_router = APIRouter(
    prefix="/api/protected",
    tags=["protected"],
    dependencies=[Depends(get_current_user)],
)


@protected_router.get("/resource1")
async def resource1():
    """Automatically protected by router dependency."""
    return {"resource": 1}


@protected_router.get("/resource2")
async def resource2():
    """Also protected."""
    return {"resource": 2}


# Admin-only router
admin_router = APIRouter(
    prefix="/api/admin",
    tags=["admin"],
    dependencies=[Depends(require_role("admin"))],
)


@admin_router.get("/stats")
async def admin_stats():
    """Admin-only endpoint."""
    return {"stats": {}}
```

### Complete CRUD Router Example

```python
# app/routers/tasks.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime
from typing import Optional

from app.database import get_session
from app.models import Task, TaskCreate, TaskUpdate, TaskRead
from app.auth import User, get_current_user

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskRead])
async def list_tasks(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    completed: Optional[bool] = None,
):
    statement = select(Task).where(Task.user_id == user.id)
    if completed is not None:
        statement = statement.where(Task.completed == completed)
    return session.exec(statement).all()


@router.post("", response_model=TaskRead, status_code=201)
async def create_task(
    data: TaskCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    task = Task(**data.model_dump(), user_id=user.id)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    task = session.get(Task, task_id)
    if not task or task.user_id != user.id:
        raise HTTPException(404, "Task not found")
    return task


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int,
    data: TaskUpdate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    task = session.get(Task, task_id)
    if not task or task.user_id != user.id:
        raise HTTPException(404, "Task not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(task, key, value)

    task.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    task = session.get(Task, task_id)
    if not task or task.user_id != user.id:
        raise HTTPException(404, "Task not found")

    session.delete(task)
    session.commit()
```

### Usage

```
/auth.protectedRoutes [pattern]
```

**User Input**: $ARGUMENTS

Available patterns:
- `basic` - Basic protected route
- `ownership` - Resource ownership checks
- `crud` - Full CRUD operations
- `optional` - Optional authentication
- `rbac` - Role-based access control
- `permissions` - Permission-based access
- `bulk` - Bulk operations
- `pagination` - Paginated responses
