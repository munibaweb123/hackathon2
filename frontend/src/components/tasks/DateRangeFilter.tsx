'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { CalendarIcon, X } from 'lucide-react';
import { format } from 'date-fns';
import { cn } from '@/lib/utils';

interface DateRangeFilterProps {
  dueAfter?: string;
  dueBefore?: string;
  onDateRangeChange: (dueAfter?: string, dueBefore?: string) => void;
}

export function DateRangeFilter({
  dueAfter,
  dueBefore,
  onDateRangeChange,
}: DateRangeFilterProps) {
  const [isOpen, setIsOpen] = useState(false);

  const dueAfterDate = dueAfter ? new Date(dueAfter) : undefined;
  const dueBeforeDate = dueBefore ? new Date(dueBefore) : undefined;

  const handleDueAfterSelect = (date: Date | undefined) => {
    onDateRangeChange(date?.toISOString(), dueBefore);
  };

  const handleDueBeforeSelect = (date: Date | undefined) => {
    onDateRangeChange(dueAfter, date?.toISOString());
  };

  const clearDateRange = () => {
    onDateRangeChange(undefined, undefined);
    setIsOpen(false);
  };

  const hasDateFilter = dueAfter || dueBefore;

  const getDisplayText = () => {
    if (dueAfterDate && dueBeforeDate) {
      return `${format(dueAfterDate, 'MMM d')} - ${format(dueBeforeDate, 'MMM d')}`;
    }
    if (dueAfterDate) {
      return `After ${format(dueAfterDate, 'MMM d')}`;
    }
    if (dueBeforeDate) {
      return `Before ${format(dueBeforeDate, 'MMM d')}`;
    }
    return 'Due Date';
  };

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className={cn(
            'justify-start text-left font-normal',
            hasDateFilter && 'bg-primary/10'
          )}
        >
          <CalendarIcon className="mr-2 h-4 w-4" />
          {getDisplayText()}
          {hasDateFilter && (
            <X
              className="ml-2 h-4 w-4 hover:text-destructive"
              onClick={(e) => {
                e.stopPropagation();
                clearDateRange();
              }}
            />
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-auto p-4" align="start">
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium">Due After</label>
            <Calendar
              mode="single"
              selected={dueAfterDate}
              onSelect={handleDueAfterSelect}
              initialFocus
            />
          </div>
          <div className="border-t pt-4">
            <label className="text-sm font-medium">Due Before</label>
            <Calendar
              mode="single"
              selected={dueBeforeDate}
              onSelect={handleDueBeforeSelect}
              disabled={(date) => dueAfterDate ? date < dueAfterDate : false}
            />
          </div>
          {hasDateFilter && (
            <Button
              variant="outline"
              size="sm"
              className="w-full"
              onClick={clearDateRange}
            >
              Clear Date Filter
            </Button>
          )}
        </div>
      </PopoverContent>
    </Popover>
  );
}
