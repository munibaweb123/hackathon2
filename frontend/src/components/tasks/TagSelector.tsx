'use client';

import { useState, useEffect } from 'react';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from '@/components/ui/command';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Button } from '@/components/ui/button';
import { Check, Plus, X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Tag {
  id: string;
  name: string;
  color?: string;
}

interface TagSelectorProps {
  selectedTags: string[];
  allTags: Tag[];
  onTagsChange: (tagIds: string[]) => void;
  disabled?: boolean;
}

export function TagSelector({ selectedTags, allTags, onTagsChange, disabled = false }: TagSelectorProps) {
  const [open, setOpen] = useState(false);
  const [inputValue, setInputValue] = useState('');

  const selectedTagObjects = allTags.filter(tag => selectedTags.includes(tag.id));

  const handleAddTag = (tagId: string) => {
    if (!selectedTags.includes(tagId)) {
      onTagsChange([...selectedTags, tagId]);
    }
    setInputValue('');
  };

  const handleRemoveTag = (tagId: string) => {
    onTagsChange(selectedTags.filter(id => id !== tagId));
  };

  const handleCreateTag = () => {
    if (inputValue.trim() && !allTags.some(tag => tag.name.toLowerCase() === inputValue.trim().toLowerCase())) {
      // In a real app, you would create the tag via API
      // For now, we'll just add it to the selection
      // This would require backend integration to actually create the tag
      alert(`Creating new tag: ${inputValue.trim()}`);
      setInputValue('');
    }
  };

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap gap-2">
        {selectedTagObjects.map((tag) => {
          const bgColor = tag.color || '#6b7280'; // Default to gray if no color
          const textColor = isColorLight(bgColor) ? '#000000' : '#ffffff';

          return (
            <Badge
              key={tag.id}
              variant="secondary"
              style={{ backgroundColor: `${bgColor}20`, color: textColor, border: `1px solid ${bgColor}` }}
              className="flex items-center gap-1 px-2 py-1 text-xs"
            >
              {tag.name}
              {!disabled && (
                <button
                  type="button"
                  onClick={() => handleRemoveTag(tag.id)}
                  className="ml-1 rounded-full hover:opacity-70"
                  aria-label={`Remove ${tag.name} tag`}
                >
                  <X className="h-3 w-3" />
                </button>
              )}
            </Badge>
          );
        })}
      </div>

      {!disabled && (
        <Popover open={open} onOpenChange={setOpen}>
          <PopoverTrigger asChild>
            <Button
              variant="outline"
              role="combobox"
              aria-expanded={open}
              className="w-full justify-between"
              disabled={disabled}
            >
              <span className="text-muted-foreground">Select tags...</span>
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-full p-0">
            <Command>
              <CommandInput
                placeholder="Search tags..."
                value={inputValue}
                onValueChange={setInputValue}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && inputValue.trim()) {
                    handleCreateTag();
                  }
                }}
              />
              <CommandList>
                <CommandEmpty>
                  <div className="p-2">
                    <p>No tags found.</p>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="mt-2 w-full justify-start"
                      onClick={handleCreateTag}
                    >
                      <Plus className="mr-2 h-4 w-4" />
                      Create "{inputValue}"
                    </Button>
                  </div>
                </CommandEmpty>
                <CommandGroup>
                  {allTags
                    .filter(tag => !selectedTags.includes(tag.id))
                    .filter(tag =>
                      tag.name.toLowerCase().includes(inputValue.toLowerCase())
                    )
                    .map((tag) => {
                      const bgColor = tag.color || '#6b7280';
                      const textColor = isColorLight(bgColor) ? '#000000' : '#ffffff';

                      return (
                        <CommandItem
                          key={tag.id}
                          value={tag.id}
                          onSelect={(currentValue) => {
                            handleAddTag(currentValue);
                            setOpen(false);
                          }}
                          className="cursor-pointer"
                        >
                          <div
                            className={cn(
                              "mr-2 flex h-4 w-4 items-center justify-center rounded-sm border",
                              selectedTags.includes(tag.id)
                                ? "bg-primary text-primary-foreground"
                                : "opacity-50 [&_svg]:invisible"
                            )}
                            style={{ backgroundColor: bgColor, color: textColor }}
                          >
                            <Check className="h-4 w-4" />
                          </div>
                          <span style={{ color: bgColor }}>{tag.name}</span>
                        </CommandItem>
                      );
                    })}
                </CommandGroup>
              </CommandList>
            </Command>
          </PopoverContent>
        </Popover>
      )}
    </div>
  );
}

// Helper function to determine if a color is light or dark
function isColorLight(hexColor: string): boolean {
  // Remove the # if present
  const hex = hexColor.replace('#', '');

  // Convert to RGB
  const r = parseInt(hex.substring(0, 2), 16);
  const g = parseInt(hex.substring(2, 4), 16);
  const b = parseInt(hex.substring(4, 6), 16);

  // Calculate the brightness (luminance)
  const brightness = (r * 299 + g * 587 + b * 114) / 1000;

  // Return true if the color is light (brightness > 128)
  return brightness > 128;
}