# Data Model: Todo In-Memory Python Console App

## Task Entity

**Name**: Task
**Description**: A todo item with a description, unique identifier, and completion status

### Fields
- **id** (string): Unique auto-generated short code identifier (format: TSK-### where ### is a sequential number)
  - Required: Yes
  - Unique: Yes
  - Format: TSK-### (e.g., TSK-001, TSK-002)
  - Validation: Must match the format pattern

- **description** (string): The task description provided by the user
  - Required: Yes
  - Validation: Must not be empty after stripping whitespace

- **completed** (boolean): Flag indicating whether the task is completed
  - Required: Yes
  - Default: False

- **created_at** (datetime): Timestamp when the task was created
  - Required: Yes
  - Default: Current timestamp at creation

### Relationships
- No direct relationships with other entities (standalone entity)

### State Transitions
- **Incomplete → Complete**: When user marks task as complete
- **Complete → Incomplete**: When user marks task as incomplete (if this functionality is supported)

## Task List

**Name**: Task List
**Description**: A collection of tasks stored in memory during the application session

### Properties
- **tasks** (list of Task objects): The collection of all tasks
- **next_id** (integer): The next sequential number to use for generating new task IDs

### Operations
- **Add Task**: Creates a new task and adds it to the collection
- **Remove Task**: Removes a task from the collection by ID
- **Update Task**: Modifies an existing task's properties
- **Get Task**: Retrieves a task by ID
- **List All Tasks**: Returns all tasks in the collection
- **Find Tasks by Status**: Returns tasks matching a specific completion status

## Validation Rules
1. Task ID must follow the format TSK-### where ### is a 3-digit number
2. Task description must not be empty or contain only whitespace
3. Task ID must be unique within the collection
4. Task operations must reference existing task IDs (except for creation)