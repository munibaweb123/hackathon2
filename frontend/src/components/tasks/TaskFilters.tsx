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
import { Filter, X } from 'lucide-react';
import type { TaskFilters, TaskStatus, TaskPriorityFilter } from '@/types';
import { cn } from '@/lib/utils';

interface TaskFiltersComponentProps {
  filters: TaskFilters;
  onFilterChange: (filters: Partial<TaskFilters>) => void;
}

const statusLabels: Record<TaskStatus, string> = {
  all: 'All',
  pending: 'Pending',
  completed: 'Completed',
};

const priorityLabels: Record<TaskPriorityFilter, string> = {
  all: 'All',
  high: 'High',
  medium: 'Medium',
  low: 'Low',
  none: 'None',
};

const priorityColors: Record<TaskPriorityFilter, string> = {
  all: '',
  high: 'text-red-600',
  medium: 'text-yellow-600',
  low: 'text-blue-600',
  none: 'text-gray-400',
};

export function TaskFiltersComponent({ filters, onFilterChange }: TaskFiltersComponentProps) {
  const hasActiveFilters =
    filters.status !== 'all' ||
    (filters.priority && filters.priority !== 'all') ||
    (filters.tags && filters.tags.length > 0);

  const clearAllFilters = () => {
    onFilterChange({
      status: 'all',
      priority: 'all',
      tags: [],
      dueBefore: undefined,
      dueAfter: undefined,
    });
  };

  return (
    <div className="flex flex-wrap items-center gap-2">
      {/* Status Filter */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant="outline"
            size="sm"
            className={cn(filters.status !== 'all' && 'bg-primary/10')}
          >
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
          <Button
            variant="outline"
            size="sm"
            className={cn(
              filters.priority && filters.priority !== 'all' && 'bg-primary/10'
            )}
          >
            Priority:{' '}
            <span className={priorityColors[filters.priority || 'all']}>
              {priorityLabels[filters.priority || 'all']}
            </span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start">
          <DropdownMenuLabel>Filter by priority</DropdownMenuLabel>
          <DropdownMenuSeparator />
          {(Object.keys(priorityLabels) as TaskPriorityFilter[]).map((priority) => (
            <DropdownMenuItem
              key={priority}
              onClick={() => onFilterChange({ priority })}
              className={cn(
                filters.priority === priority && 'bg-accent',
                priorityColors[priority]
              )}
            >
              {priorityLabels[priority]}
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Clear Filters Button */}
      {hasActiveFilters && (
        <Button
          variant="ghost"
          size="sm"
          onClick={clearAllFilters}
          className="text-muted-foreground hover:text-foreground"
        >
          <X className="mr-1 h-4 w-4" />
          Clear Filters
        </Button>
      )}
    </div>
  );
}

// Re-export original TaskFilters for backwards compatibility
export { TaskFiltersComponent as TaskFilters };
