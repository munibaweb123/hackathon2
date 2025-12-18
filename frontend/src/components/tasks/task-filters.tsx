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
import type { TaskFilters, TaskStatus, TaskSortBy, SortOrder } from '@/types';

interface TaskFiltersProps {
  filters: TaskFilters;
  onFilterChange: (filters: Partial<TaskFilters>) => void;
}

const statusLabels: Record<TaskStatus, string> = {
  all: 'All Tasks',
  pending: 'Pending',
  completed: 'Completed',
};

const sortLabels: Record<TaskSortBy, string> = {
  created_at: 'Date Created',
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
