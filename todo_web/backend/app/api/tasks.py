"""Task API endpoints - CRUD operations for todo items."""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, col

from ..core.database import get_session
from ..core.auth import get_current_user, verify_user_access, AuthenticatedUser
from ..models.task import Task, Priority, RecurrencePattern
from ..schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
from ..utils.recurrence import generate_recurring_tasks

router = APIRouter()


@router.get("/{user_id}/tasks", response_model=TaskListResponse)
async def list_tasks(
    user_id: str,
    status_filter: Optional[str] = Query(None, alias="status"),
    sort_by: str = Query("created_at", alias="sort"),
    order: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    include_recurring: bool = Query(True, description="Include recurring task instances"),
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TaskListResponse:
    """
    List all tasks for a user with optional filtering and sorting.

    - **status**: Filter by 'completed' or 'pending'
    - **sort**: Sort by 'created_at', 'due_date', 'priority', or 'title'
    - **order**: 'asc' or 'desc'
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 50, max: 100)
    - **include_recurring**: Whether to include recurring task instances (default: True)
    """
    # Verify user access
    verify_user_access(user_id, current_user)

    # Build query
    statement = select(Task).where(Task.user_id == user_id)

    # Don't include parent recurring tasks if we're showing instances separately
    if include_recurring:
        statement = statement.where((Task.is_recurring == False) | (Task.parent_task_id.is_(None)))
    else:
        statement = statement.where(Task.is_recurring == False)

    # Apply status filter
    if status_filter == "completed":
        statement = statement.where(Task.completed == True)
    elif status_filter == "pending":
        statement = statement.where(Task.completed == False)

    # Get total count before pagination
    count_statement = select(Task).where(Task.user_id == user_id)
    if include_recurring:
        count_statement = count_statement.where((Task.is_recurring == False) | (Task.parent_task_id.is_(None)))
    else:
        count_statement = count_statement.where(Task.is_recurring == False)

    if status_filter == "completed":
        count_statement = count_statement.where(Task.completed == True)
    elif status_filter == "pending":
        count_statement = count_statement.where(Task.completed == False)

    total = len(session.exec(count_statement).all())

    # Apply sorting
    sort_column = {
        "created_at": Task.created_at,
        "due_date": Task.due_date,
        "priority": Task.priority,
        "title": Task.title,
    }.get(sort_by, Task.created_at)

    if order == "asc":
        statement = statement.order_by(col(sort_column).asc())
    else:
        statement = statement.order_by(col(sort_column).desc())

    # Apply pagination
    offset = (page - 1) * page_size
    statement = statement.offset(offset).limit(page_size)

    # Execute query
    tasks = session.exec(statement).all()

    return TaskListResponse(
        tasks=[TaskResponse.model_validate(task) for task in tasks],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/{user_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TaskResponse:
    """
    Create a new task for the user.

    - **title**: Task title (required)
    - **description**: Task description (optional)
    - **priority**: low, medium, or high (default: medium)
    - **due_date**: Due date in ISO format (optional)
    - **is_recurring**: Whether the task repeats (default: False)
    - **recurrence_pattern**: daily, weekly, biweekly, monthly, yearly, or custom (required if recurring)
    - **recurrence_interval**: How often to repeat (e.g., every 2 weeks) (default: 1)
    - **recurrence_end_date**: When to stop recurring (optional)
    """
    # Verify user access
    verify_user_access(user_id, current_user)

    # Validate recurrence fields if task is recurring
    if task_data.is_recurring:
        if not task_data.recurrence_pattern:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="recurrence_pattern is required for recurring tasks"
            )
        if task_data.recurrence_interval is not None and task_data.recurrence_interval < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="recurrence_interval must be at least 1"
            )

    # Create task
    task = Task(
        title=task_data.title,
        description=task_data.description,
        priority=Priority(task_data.priority.value),
        due_date=task_data.due_date,
        user_id=user_id,
        is_recurring=task_data.is_recurring,
        recurrence_pattern=task_data.recurrence_pattern,
        recurrence_interval=task_data.recurrence_interval,
        recurrence_end_date=task_data.recurrence_end_date,
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    # If this is a recurring task, generate the next few instances
    if task_data.is_recurring and task_data.due_date:
        # Convert the task to a dictionary for the recurrence utility
        task_dict = {
            'title': task.title,
            'description': task.description,
            'priority': task.priority.value,
            'due_date': task.due_date,
            'user_id': task.user_id,
            'is_recurring': task.is_recurring,
            'recurrence_pattern': task.recurrence_pattern,
            'recurrence_interval': task.recurrence_interval,
            'recurrence_end_date': task.recurrence_end_date,
        }

        # Generate recurring instances
        recurring_instances = generate_recurring_tasks(
            original_task_data=task_dict,
            start_date=task.due_date,
            end_date=task.recurrence_end_date,
            max_instances=5  # Generate up to 5 future instances
        )

        # Create the recurring instances
        for instance_data in recurring_instances[1:]:  # Skip the first one since that's the original
            instance_task = Task(
                title=instance_data['title'],
                description=instance_data['description'],
                priority=Priority(instance_data['priority']),
                due_date=instance_data['due_date'],
                user_id=instance_data['user_id'],
                is_recurring=False,  # The instance itself is not recurring
                parent_task_id=task.id,  # Link to the parent recurring task
                completed=instance_data['completed'],
            )
            session.add(instance_task)

        session.commit()

    return TaskResponse.model_validate(task)


@router.get("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    user_id: str,
    task_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TaskResponse:
    """Get a specific task by ID."""
    # Verify user access
    verify_user_access(user_id, current_user)

    # Get task
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return TaskResponse.model_validate(task)


@router.put("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: str,
    task_id: int,
    task_data: TaskUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TaskResponse:
    """
    Update an existing task.

    Only provided fields will be updated.
    """
    # Verify user access
    verify_user_access(user_id, current_user)

    # Get task
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Validate recurrence fields if task is being updated to recurring
    # If is_recurring is being set to True (and it wasn't already True), validate required recurrence fields
    if task_data.is_recurring is True and task.is_recurring is False:
        if task_data.recurrence_pattern is None:  # Field is being updated to recurring but no pattern provided
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="recurrence_pattern is required for recurring tasks"
            )
        if task_data.recurrence_interval is not None and task_data.recurrence_interval < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="recurrence_interval must be at least 1"
            )

    # Check if we're updating recurrence fields for a recurring task
    is_recurring_updated = task_data.is_recurring is not None
    is_recurrence_pattern_updated = task_data.recurrence_pattern is not None

    # Update only provided fields
    update_data = task_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "priority" and value is not None:
            setattr(task, key, Priority(value.value))
        elif key == "recurrence_pattern" and value is not None:
            setattr(task, key, RecurrencePattern(value))
        else:
            setattr(task, key, value)

    task.updated_at = datetime.utcnow()

    # If this is a recurring task and recurrence fields were updated, regenerate instances
    if (is_recurring_updated or is_recurrence_pattern_updated) and task.is_recurring:
        # Delete existing recurring instances for this parent task
        delete_statement = select(Task).where(Task.parent_task_id == task.id)
        instances = session.exec(delete_statement).all()
        for instance in instances:
            session.delete(instance)

        # Regenerate recurring instances if the task is still recurring
        if task.is_recurring and task.due_date:
            task_dict = {
                'title': task.title,
                'description': task.description,
                'priority': task.priority.value,
                'due_date': task.due_date,
                'user_id': task.user_id,
                'is_recurring': task.is_recurring,
                'recurrence_pattern': task.recurrence_pattern,
                'recurrence_interval': task.recurrence_interval,
                'recurrence_end_date': task.recurrence_end_date,
            }

            recurring_instances = generate_recurring_tasks(
                original_task_data=task_dict,
                start_date=task.due_date,
                end_date=task.recurrence_end_date,
                max_instances=5
            )

            # Create the recurring instances (skip original)
            for instance_data in recurring_instances[1:]:
                instance_task = Task(
                    title=instance_data['title'],
                    description=instance_data['description'],
                    priority=Priority(instance_data['priority']),
                    due_date=instance_data['due_date'],
                    user_id=instance_data['user_id'],
                    is_recurring=False,
                    parent_task_id=task.id,
                    completed=instance_data['completed'],
                )
                session.add(instance_task)

    session.add(task)
    session.commit()
    session.refresh(task)

    return TaskResponse.model_validate(task)


@router.delete("/{user_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: str,
    task_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> None:
    """Delete a task."""
    # Verify user access
    verify_user_access(user_id, current_user)

    # Get task
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # If this is a recurring parent task, also delete all its instances
    if task.is_recurring:
        # Delete all recurring instances of this task
        instance_statement = select(Task).where(Task.parent_task_id == task.id)
        instances = session.exec(instance_statement).all()
        for instance in instances:
            session.delete(instance)

    session.delete(task)
    session.commit()


@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=TaskResponse)
async def toggle_task_completion(
    user_id: str,
    task_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TaskResponse:
    """Toggle task completion status."""
    # Verify user access
    verify_user_access(user_id, current_user)

    # Get task
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Toggle completion
    task.completed = not task.completed
    task.updated_at = datetime.utcnow()

    # If this is a recurring task instance, create the next instance
    if task.parent_task_id:
        parent_statement = select(Task).where(Task.id == task.parent_task_id)
        parent_task = session.exec(parent_statement).first()

        if parent_task and parent_task.is_recurring and parent_task.recurrence_pattern:
            from ..utils.recurrence import calculate_next_occurrence

            # Calculate next occurrence
            next_due_date = calculate_next_occurrence(
                start_date=task.due_date,
                pattern=RecurrencePattern(parent_task.recurrence_pattern),
                interval=parent_task.recurrence_interval or 1
            )

            # Check if we've reached the recurrence end date
            if (not parent_task.recurrence_end_date or
                next_due_date <= parent_task.recurrence_end_date):
                # Create next recurring instance
                next_instance = Task(
                    title=parent_task.title,
                    description=parent_task.description,
                    priority=parent_task.priority,
                    due_date=next_due_date,
                    user_id=parent_task.user_id,
                    is_recurring=False,
                    parent_task_id=parent_task.id,
                    completed=False,
                )
                session.add(next_instance)

    session.add(task)
    session.commit()
    session.refresh(task)

    return TaskResponse.model_validate(task)
