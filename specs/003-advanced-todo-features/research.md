# Research: Advanced Todo Features

**Feature**: 003-advanced-todo-features
**Date**: 2025-12-09
**Status**: Complete

## Research Tasks

### 1. Recurrence Pattern Calculation

**Question**: How to calculate next occurrence dates for daily/weekly/monthly/custom patterns?

**Decision**: Use `python-dateutil` library with its `relativedelta` and `rrule` modules.

**Rationale**:
- Standard library `datetime` lacks robust recurring date support
- `python-dateutil` handles edge cases (month-end, leap years, DST)
- Well-maintained, BSD-licensed, widely used
- `rrule` follows iCalendar RFC 5545 standard for recurrence

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Manual calculation with `datetime` | Error-prone for edge cases (Feb 30, etc.) |
| `croniter` | Designed for cron expressions, not calendar patterns |
| `recurring-ical-events` | Overkill for our simple use case |

**Implementation Pattern**:
```python
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY

# Weekly on Monday example
next_date = current_date + relativedelta(weeks=1, weekday=MO)

# Or using rrule for complex patterns
rule = rrule(WEEKLY, byweekday=MO, dtstart=start_date, count=2)
next_occurrence = list(rule)[1]
```

---

### 2. Time Zone Handling

**Question**: How to store and display times across timezones?

**Decision**: Store all datetimes as UTC ISO 8601 strings, display in local timezone.

**Rationale**:
- Consistent storage format (existing pattern in the app)
- Avoids timezone database dependencies for storage
- Python's `datetime.timezone` handles UTC conversion
- `python-dateutil` provides robust timezone parsing

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Store as local time | Breaks when user travels/changes timezone |
| Store Unix timestamps | Less human-readable in JSON |
| Use pytz | Deprecated in favor of Python 3.9+ zoneinfo |

**Implementation Pattern**:
```python
from datetime import datetime, timezone

# Store in UTC
utc_time = datetime.now(timezone.utc).isoformat()

# Display in local
local_time = datetime.fromisoformat(utc_time).astimezone()
```

---

### 3. Console Notification Strategy

**Question**: How to implement reminders in a console application?

**Decision**: Check for due reminders on app startup and after each action, display as rich console alerts.

**Rationale**:
- Console apps cannot push notifications when closed
- Checking on startup catches all missed reminders
- Rich library provides styled alert boxes
- Simple, no background process needed

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Background daemon | Over-complex for hackathon scope |
| System notifications (notify-send, etc.) | Platform-specific, external dependencies |
| Desktop notification libraries (plyer) | Adds dependency, still needs app running |

**Implementation Pattern**:
```python
# On app startup and after actions
due_reminders = reminder_service.check_due_reminders()
for reminder in due_reminders:
    console.print(Panel(f"⏰ Reminder: {task.title}", style="yellow"))
    reminder_service.mark_as_shown(reminder)
```

---

### 4. Recurring Task Series Management

**Question**: How to track which tasks belong to the same recurring series?

**Decision**: Use a `series_id` UUID field linking all instances of a recurring task.

**Rationale**:
- Allows "edit all future" and "delete all" operations
- UUID ensures uniqueness without central counter
- Original task becomes the template, new instances reference it
- Preserves history of completed instances

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Parent-child relationship | Complex, breaks if parent deleted |
| Only track the pattern, generate instances on-the-fly | Loses history of past completions |
| Tag-based grouping | Conflicts with user categories |

**Implementation Pattern**:
```python
@dataclass
class Task:
    # ... existing fields ...
    series_id: Optional[str] = None  # UUID for recurring series
    recurrence: Optional[RecurrencePattern] = None
```

---

### 5. JSON Schema Backward Compatibility

**Question**: How to extend tasks.json without breaking existing data?

**Decision**: All new fields are optional with sensible defaults.

**Rationale**:
- Existing tasks.json files will load without errors
- New fields default to `None` or empty values
- Schema version in metadata allows future migrations
- `from_dict` already handles missing keys gracefully

**Migration Strategy**:
1. New fields added as `Optional` with `None` default
2. `from_dict` uses `.get()` with fallbacks
3. Schema version bumped from 1.0 to 1.1
4. No migration script needed - lazy upgrade on first save

---

### 6. Time Input Parsing

**Question**: How to accept flexible time input (12h/24h format)?

**Decision**: Use `python-dateutil.parser` for flexible time parsing.

**Rationale**:
- Accepts "2:30pm", "14:30", "2:30 PM", "14:30:00"
- Already adding python-dateutil for recurrence
- Battle-tested parsing logic
- Locale-aware

**Implementation Pattern**:
```python
from dateutil.parser import parse

# Flexible parsing
time = parse("2:30pm").time()  # datetime.time(14, 30)
time = parse("14:30").time()   # datetime.time(14, 30)
```

---

## Dependency Addition

**New Dependency**: `python-dateutil>=2.8.0`

**Justification**:
- Required for recurrence calculation (rrule)
- Required for flexible time parsing
- Required for relativedelta date math
- Well-maintained, BSD license, no transitive dependencies

**pyproject.toml update**:
```toml
dependencies = [
    "rich>=14.2.0",
    "python-dateutil>=2.8.0",  # NEW
]
```

---

## Summary

| Research Area | Decision | Confidence |
|---------------|----------|------------|
| Recurrence calculation | python-dateutil rrule/relativedelta | High |
| Timezone handling | Store UTC, display local | High |
| Console notifications | Check on startup/action, rich Panel | High |
| Series management | series_id UUID field | High |
| Backward compatibility | Optional fields with defaults | High |
| Time parsing | dateutil.parser | High |

All NEEDS CLARIFICATION items resolved. Ready for Phase 1 design.
