'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import { Tag } from '@/types';

// Mock API functions - replace with actual API calls
const mockGetTags = async (): Promise<Tag[]> => {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 500));
  return [
    { id: '1', name: 'Work', color: '#3b82f6', user_id: 'user1', created_at: '2024-01-01', updated_at: '2024-01-01' },
    { id: '2', name: 'Personal', color: '#ef4444', user_id: 'user1', created_at: '2024-01-02', updated_at: '2024-01-02' },
    { id: '3', name: 'Shopping', color: '#10b981', user_id: 'user1', created_at: '2024-01-03', updated_at: '2024-01-03' },
  ];
};

const mockCreateTag = async (name: string, color: string): Promise<Tag> => {
  await new Promise(resolve => setTimeout(resolve, 500));
  return {
    id: Math.random().toString(36).substring(7),
    name,
    color,
    user_id: 'user1',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  };
};

const mockUpdateTag = async (id: string, name: string, color: string): Promise<Tag> => {
  await new Promise(resolve => setTimeout(resolve, 500));
  return {
    id,
    name,
    color,
    user_id: 'user1',
    created_at: '2024-01-01',
    updated_at: new Date().toISOString(),
  };
};

const mockDeleteTag = async (id: string): Promise<boolean> => {
  await new Promise(resolve => setTimeout(resolve, 500));
  return true;
};

export default function TagsPage() {
  const [tags, setTags] = useState<Tag[]>([]);
  const [loading, setLoading] = useState(true);
  const [newTagName, setNewTagName] = useState('');
  const [newTagColor, setNewTagColor] = useState('#3b82f6');
  const [editingTag, setEditingTag] = useState<Tag | null>(null);
  const [editTagName, setEditTagName] = useState('');
  const [editTagColor, setEditTagColor] = useState('#3b82f6');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    fetchTags();
  }, []);

  const fetchTags = async () => {
    try {
      setLoading(true);
      const fetchedTags = await mockGetTags();
      setTags(fetchedTags);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to fetch tags',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTag = async () => {
    if (!newTagName.trim()) {
      toast({
        title: 'Error',
        description: 'Tag name is required',
        variant: 'destructive',
      });
      return;
    }

    try {
      const newTag = await mockCreateTag(newTagName, newTagColor);
      setTags([...tags, newTag]);
      setNewTagName('');
      setNewTagColor('#3b82f6');
      setIsCreateDialogOpen(false);
      toast({
        title: 'Success',
        description: 'Tag created successfully',
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to create tag',
        variant: 'destructive',
      });
    }
  };

  const handleUpdateTag = async () => {
    if (!editingTag || !editTagName.trim()) {
      toast({
        title: 'Error',
        description: 'Tag name is required',
        variant: 'destructive',
      });
      return;
    }

    try {
      const updatedTag = await mockUpdateTag(editingTag.id, editTagName, editTagColor);
      setTags(tags.map(tag => tag.id === editingTag.id ? updatedTag : tag));
      setEditingTag(null);
      setEditTagName('');
      setEditTagColor('#3b82f6');
      setIsEditDialogOpen(false);
      toast({
        title: 'Success',
        description: 'Tag updated successfully',
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to update tag',
        variant: 'destructive',
      });
    }
  };

  const handleDeleteTag = async (id: string) => {
    try {
      await mockDeleteTag(id);
      setTags(tags.filter(tag => tag.id !== id));
      toast({
        title: 'Success',
        description: 'Tag deleted successfully',
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to delete tag',
        variant: 'destructive',
      });
    }
  };

  const handleEditClick = (tag: Tag) => {
    setEditingTag(tag);
    setEditTagName(tag.name);
    setEditTagColor(tag.color || '#3b82f6');
    setIsEditDialogOpen(true);
  };

  // Helper function to determine if a color is light or dark
  const isColorLight = (hexColor: string): boolean => {
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
  };

  return (
    <div className="container mx-auto py-8">
      <div className="max-w-4xl mx-auto">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-2xl">Tag Management</CardTitle>
            <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
              <DialogTrigger asChild>
                <Button>Add Tag</Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create New Tag</DialogTitle>
                  <DialogDescription>
                    Add a new tag with a name and color to organize your tasks.
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="tag-name">Tag Name</Label>
                    <Input
                      id="tag-name"
                      value={newTagName}
                      onChange={(e) => setNewTagName(e.target.value)}
                      placeholder="Enter tag name"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="tag-color">Tag Color</Label>
                    <Input
                      id="tag-color"
                      type="color"
                      value={newTagColor}
                      onChange={(e) => setNewTagColor(e.target.value)}
                      className="h-10 w-full cursor-pointer"
                    />
                  </div>
                </div>
                <div className="flex justify-end gap-2">
                  <Button
                    variant="outline"
                    onClick={() => {
                      setIsCreateDialogOpen(false);
                      setNewTagName('');
                      setNewTagColor('#3b82f6');
                    }}
                  >
                    Cancel
                  </Button>
                  <Button onClick={handleCreateTag}>Create Tag</Button>
                </div>
              </DialogContent>
            </Dialog>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex justify-center py-8">
                <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-primary"></div>
              </div>
            ) : tags.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <p>No tags found. Create your first tag to get started.</p>
              </div>
            ) : (
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {tags.map((tag) => {
                  const bgColor = tag.color || '#6b7280'; // Default to gray if no color
                  const textColor = isColorLight(bgColor) ? '#000000' : '#ffffff';

                  return (
                    <div
                      key={tag.id}
                      className="flex items-center justify-between p-4 rounded-lg border bg-card shadow-sm"
                    >
                      <div className="flex items-center gap-3">
                        <Badge
                          variant="secondary"
                          style={{ backgroundColor: `${bgColor}20`, color: textColor, border: `1px solid ${bgColor}` }}
                          className="px-3 py-1"
                        >
                          {tag.name}
                        </Badge>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEditClick(tag)}
                        >
                          Edit
                        </Button>
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={() => handleDeleteTag(tag.id)}
                        >
                          Delete
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Edit Tag Dialog */}
        <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Edit Tag</DialogTitle>
              <DialogDescription>
                Update the name and color of the tag.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="edit-tag-name">Tag Name</Label>
                <Input
                  id="edit-tag-name"
                  value={editTagName}
                  onChange={(e) => setEditTagName(e.target.value)}
                  placeholder="Enter tag name"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-tag-color">Tag Color</Label>
                <Input
                  id="edit-tag-color"
                  type="color"
                  value={editTagColor}
                  onChange={(e) => setEditTagColor(e.target.value)}
                  className="h-10 w-full cursor-pointer"
                />
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                onClick={() => {
                  setIsEditDialogOpen(false);
                  setEditingTag(null);
                  setEditTagName('');
                  setEditTagColor('#3b82f6');
                }}
              >
                Cancel
              </Button>
              <Button onClick={handleUpdateTag}>Update Tag</Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}