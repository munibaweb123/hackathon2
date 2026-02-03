'use client';

import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import type { TaskSortBy, SortOrder } from '@/types';

interface SortSelectorProps {
  sortBy: TaskSortBy;
  sortOrder: SortOrder;
  onSortChange: (sortBy: TaskSortBy, order: SortOrder) => void;
}

export function SortSelector({ sortBy, sortOrder, onSortChange }: SortSelectorProps) {
  const sortOptions = [
    { value: 'created_at', label: 'Date Created' },
    { value: 'due_date', label: 'Due Date' },
    { value: 'priority', label: 'Priority' },
    { value: 'title', label: 'Title' },
  ];

  const handleSortByChange = (value: string) => {
    onSortChange(value as TaskSortBy, sortOrder);
  };

  const handleSortOrderChange = (value: string) => {
    onSortChange(sortBy, value as SortOrder);
  };

  return (
    <div className="flex items-center gap-2">
      <Select value={sortBy} onValueChange={handleSortByChange}>
        <SelectTrigger className="w-[180px]">
          <SelectValue placeholder="Sort by" />
        </SelectTrigger>
        <SelectContent>
          {sortOptions.map((option) => (
            <SelectItem key={option.value} value={option.value}>
              {option.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Select value={sortOrder} onValueChange={handleSortOrderChange}>
        <SelectTrigger className="w-[100px]">
          <SelectValue placeholder="Order" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="asc">Ascending</SelectItem>
          <SelectItem value="desc">Descending</SelectItem>
        </SelectContent>
      </Select>
    </div>
  );
}