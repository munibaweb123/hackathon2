'use client';

import { useState, useEffect, useRef } from 'react';
import { Input } from '@/components/ui/input';
import { Search } from 'lucide-react';

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  delay?: number;
}

export function SearchBar({ value, onChange, placeholder = 'Search tasks...', delay = 300 }: SearchBarProps) {
  const [inputValue, setInputValue] = useState(value);
  const onChangeRef = useRef(onChange);
  const previousValueRef = useRef(value);

  // Keep the ref updated with the latest onChange
  useEffect(() => {
    onChangeRef.current = onChange;
  }, [onChange]);

  // Update local input when external value changes
  useEffect(() => {
    setInputValue(value);
    previousValueRef.current = value;
  }, [value]);

  // Debounced search effect - only call onChange if value actually changed
  useEffect(() => {
    const handler = setTimeout(() => {
      if (inputValue !== previousValueRef.current) {
        previousValueRef.current = inputValue;
        onChangeRef.current(inputValue);
      }
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [inputValue, delay]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  };

  return (
    <div className="relative w-full max-w-sm">
      <Search className="absolute left-2 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
      <Input
        type="search"
        placeholder={placeholder}
        value={inputValue}
        onChange={handleChange}
        className="pl-8"
      />
    </div>
  );
}