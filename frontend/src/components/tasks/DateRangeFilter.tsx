'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { CalendarIcon } from 'lucide-react';
import { cn } from '@/lib/utils';
import { format } from 'date-fns';

interface DateRangeFilterProps {
  startDate: Date | undefined;
  endDate: Date | undefined;
  onStartDateChange: (date: Date | undefined) => void;
  onEndDateChange: (date: Date | undefined) => void;
}

export function DateRangeFilter({
  startDate,
  endDate,
  onStartDateChange,
  onEndDateChange,
}: DateRangeFilterProps) {
  const [openStart, setOpenStart] = useState(false);
  const [openEnd, setOpenEnd] = useState(false);

  return (
    <div className="flex flex-wrap gap-2">
      {/* Start Date Filter */}
      <Popover open={openStart} onOpenChange={setOpenStart}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            className={cn(
              'w-[200px] justify-start text-left font-normal',
              !startDate && 'text-muted-foreground'
            )}
          >
            <CalendarIcon className="mr-2 h-4 w-4" />
            {startDate ? format(startDate, 'PPP') : <span>Start date</span>}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0" align="start">
          <Calendar
            mode="single"
            selected={startDate}
            onSelect={(date) => {
              onStartDateChange(date);
              setOpenStart(false);
            }}
            disabled={endDate ? [{ after: new Date(endDate) }] : undefined}
            initialFocus
          />
        </PopoverContent>
      </Popover>

      {/* End Date Filter */}
      <Popover open={openEnd} onOpenChange={setOpenEnd}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            className={cn(
              'w-[200px] justify-start text-left font-normal',
              !endDate && 'text-muted-foreground'
            )}
          >
            <CalendarIcon className="mr-2 h-4 w-4" />
            {endDate ? format(endDate, 'PPP') : <span>End date</span>}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0" align="start">
          <Calendar
            mode="single"
            selected={endDate}
            onSelect={(date) => {
              onEndDateChange(date);
              setOpenEnd(false);
            }}
            disabled={startDate ? [{ before: new Date(startDate) }] : undefined}
            initialFocus
          />
        </PopoverContent>
      </Popover>

      {/* Clear Dates Button */}
      {(startDate || endDate) && (
        <Button
          variant="outline"
          size="sm"
          onClick={() => {
            onStartDateChange(undefined);
            onEndDateChange(undefined);
          }}
        >
          Clear
        </Button>
      )}
    </div>
  );
}