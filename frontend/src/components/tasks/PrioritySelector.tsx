'use client';

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';

interface PrioritySelectorProps {
  priority: 'low' | 'medium' | 'high' | 'none';
  onPriorityChange: (priority: 'low' | 'medium' | 'high' | 'none') => void;
  disabled?: boolean;
}

export function PrioritySelector({ priority, onPriorityChange, disabled = false }: PrioritySelectorProps) {
  const priorityOptions = [
    { value: 'none', label: 'No Priority', color: 'text-gray-500' },
    { value: 'low', label: 'Low', color: 'text-green-600' },
    { value: 'medium', label: 'Medium', color: 'text-yellow-600' },
    { value: 'high', label: 'High', color: 'text-red-600' },
  ];

  const selectedOption = priorityOptions.find(option => option.value === priority) || priorityOptions[0];

  return (
    <div className="space-y-2">
      <Label htmlFor="priority">Priority</Label>
      <Select value={priority} onValueChange={onPriorityChange} disabled={disabled}>
        <SelectTrigger id="priority" className={`w-full ${selectedOption.color}`}>
          <SelectValue placeholder="Select priority" />
        </SelectTrigger>
        <SelectContent>
          {priorityOptions.map((option) => (
            <SelectItem
              key={option.value}
              value={option.value}
              className={option.color}
            >
              {option.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}