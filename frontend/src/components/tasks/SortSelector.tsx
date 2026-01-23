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
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';
import type { TaskSortBy, SortOrder } from '@/types';

interface SortSelectorProps {
  sortBy: TaskSortBy;
  order: SortOrder;
  onSortChange: (sortBy: TaskSortBy, order: SortOrder) => void;
}

const sortLabels: Record<TaskSortBy, string> = {
  created_at: 'Date Created',
  updated_at: 'Last Updated',
  due_date: 'Due Date',
  priority: 'Priority',
  title: 'Title',
};

export function SortSelector({ sortBy, order, onSortChange }: SortSelectorProps) {
  const toggleOrder = () => {
    onSortChange(sortBy, order === 'asc' ? 'desc' : 'asc');
  };

  return (
    <div className="flex items-center gap-1">
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="sm">
            <ArrowUpDown className="mr-2 h-4 w-4" />
            {sortLabels[sortBy]}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuLabel>Sort by</DropdownMenuLabel>
          <DropdownMenuSeparator />
          {(Object.keys(sortLabels) as TaskSortBy[]).map((sort) => (
            <DropdownMenuItem
              key={sort}
              onClick={() => onSortChange(sort, order)}
              className={sortBy === sort ? 'bg-accent' : ''}
            >
              {sortLabels[sort]}
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>

      <Button variant="outline" size="sm" onClick={toggleOrder}>
        {order === 'asc' ? (
          <ArrowUp className="h-4 w-4" />
        ) : (
          <ArrowDown className="h-4 w-4" />
        )}
      </Button>
    </div>
  );
}
