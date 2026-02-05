'use client';

import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import type { TaskFilters, TaskStatus, TaskSortBy, TaskPriorityFilter } from '@/types';

interface TaskFiltersProps {
  filters: TaskFilters;
  onFilterChange: (filters: Partial<TaskFilters>) => void;
}

const statusLabels: Record<TaskStatus, string> = {
  all: 'All Tasks',
  pending: 'Pending',
  completed: 'Completed',
};

const priorityLabels: Record<TaskPriorityFilter, string> = {
  all: 'All Priorities',
  none: 'No Priority',
  low: 'Low Priority',
  medium: 'Medium Priority',
  high: 'High Priority',
};

const sortLabels: Record<TaskSortBy, string> = {
  created_at: 'Date Created',
  updated_at: 'Date Updated',
  due_date: 'Due Date',
  priority: 'Priority',
  title: 'Title',
};

export function TaskFilters({ filters, onFilterChange }: TaskFiltersProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {/* Status Filter */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="sm">
            Status: {statusLabels[filters.status]}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start">
          <DropdownMenuLabel>Filter by status</DropdownMenuLabel>
          <DropdownMenuSeparator />
          {(Object.keys(statusLabels) as TaskStatus[]).map((status) => (
            <DropdownMenuItem
              key={status}
              onClick={() => onFilterChange({ status })}
              className={filters.status === status ? 'bg-accent' : ''}
            >
              {statusLabels[status]}
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Priority Filter */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="sm">
            Priority: {priorityLabels[filters.priority || 'all']}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start">
          <DropdownMenuLabel>Filter by priority</DropdownMenuLabel>
          <DropdownMenuSeparator />
          {(Object.keys(priorityLabels) as TaskPriorityFilter[]).map((priority) => (
            <DropdownMenuItem
              key={priority}
              onClick={() => onFilterChange({ priority })}
              className={(filters.priority || 'all') === priority ? 'bg-accent' : ''}
            >
              {priorityLabels[priority]}
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Sort By Filter */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="sm">
            Sort: {sortLabels[filters.sortBy]}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start">
          <DropdownMenuLabel>Sort by</DropdownMenuLabel>
          <DropdownMenuSeparator />
          {(Object.keys(sortLabels) as TaskSortBy[]).map((sortBy) => (
            <DropdownMenuItem
              key={sortBy}
              onClick={() => onFilterChange({ sortBy })}
              className={filters.sortBy === sortBy ? 'bg-accent' : ''}
            >
              {sortLabels[sortBy]}
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Order Toggle */}
      <Button
        variant="outline"
        size="sm"
        onClick={() =>
          onFilterChange({ order: filters.order === 'asc' ? 'desc' : 'asc' })
        }
      >
        {filters.order === 'asc' ? '↑ Ascending' : '↓ Descending'}
      </Button>
    </div>
  );
}
