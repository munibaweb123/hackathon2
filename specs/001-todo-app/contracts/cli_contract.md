# API Contract: Todo In-Memory Python Console App

## CLI Command Interface

### Add Task
- **Command**: `add <description>`
- **Input**: Task description (string)
- **Output**: Task object with ID and success message
- **Success Response**:
  ```
  Task added successfully: TSK-001 - <description>
  ```
- **Error Response**:
  ```
  Error: Task description cannot be empty
  ```

### List Tasks
- **Command**: `list` or `view`
- **Input**: None
- **Output**: List of all tasks with their status
- **Success Response**:
  ```
  Task List:
  TSK-001 [ ] Complete project documentation
  TSK-002 [x] Review code changes
  ```
- **Error Response**: N/A

### Complete Task
- **Command**: `complete <task_id>`
- **Input**: Task ID (string in TSK-### format)
- **Output**: Success message or error
- **Success Response**:
  ```
  Task TSK-001 marked as complete
  ```
- **Error Response**:
  ```
  Error: Task TSK-001 not found
  ```

### Update Task
- **Command**: `update <task_id> <new_description>`
- **Input**: Task ID (string) and new description (string)
- **Output**: Success message or error
- **Success Response**:
  ```
  Task TSK-001 updated: <new_description>
  ```
- **Error Response**:
  ```
  Error: Task TSK-001 not found
  ```
  or
  ```
  Error: Task description cannot be empty
  ```

### Delete Task
- **Command**: `delete <task_id>`
- **Input**: Task ID (string in TSK-### format)
- **Output**: Success message or error
- **Success Response**:
  ```
  Task TSK-001 deleted successfully
  ```
- **Error Response**:
  ```
  Error: Task TSK-001 not found
  ```