'use client';

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { RecurrencePattern } from '@/types';

interface RecurrenceSelectorProps {
  recurrencePattern: RecurrencePattern | null;
  recurrenceInterval: number;
  onPatternChange: (pattern: RecurrencePattern | null) => void;
  onIntervalChange: (interval: number) => void;
  disabled?: boolean;
}

export function RecurrenceSelector({
  recurrencePattern,
  recurrenceInterval,
  onPatternChange,
  onIntervalChange,
  disabled = false,
}: RecurrenceSelectorProps) {
  const recurrenceOptions: { value: RecurrencePattern; label: string }[] = [
    { value: 'daily', label: 'Daily' },
    { value: 'weekly', label: 'Weekly' },
    { value: 'biweekly', label: 'Bi-weekly' },
    { value: 'monthly', label: 'Monthly' },
    { value: 'yearly', label: 'Yearly' },
    { value: 'custom', label: 'Custom' },
  ];

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="recurrence_pattern">Recurrence Pattern</Label>
        <Select
          value={recurrencePattern || ''}
          onValueChange={(value) => onPatternChange(value as RecurrencePattern)}
          disabled={disabled}
        >
          <SelectTrigger id="recurrence_pattern">
            <SelectValue placeholder="Select pattern" />
          </SelectTrigger>
          <SelectContent>
            {recurrenceOptions.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <Label htmlFor="recurrence_interval">Repeat Every</Label>
        <div className="flex items-center space-x-2">
          <Input
            id="recurrence_interval"
            type="number"
            min="1"
            value={recurrenceInterval}
            onChange={(e) => onIntervalChange(parseInt(e.target.value) || 1)}
            disabled={disabled}
            className="max-w-[120px]"
          />
          <span className="text-sm text-muted-foreground">
            {recurrencePattern === 'daily' && 'day(s)'}
            {recurrencePattern === 'weekly' && 'week(s)'}
            {recurrencePattern === 'biweekly' && 'bi-week(s)'}
            {recurrencePattern === 'monthly' && 'month(s)'}
            {recurrencePattern === 'yearly' && 'year(s)'}
            {recurrencePattern === 'custom' && 'period(s)'}
          </span>
        </div>
        <p className="text-xs text-muted-foreground">e.g., every 2 weeks</p>
      </div>
    </div>
  );
}