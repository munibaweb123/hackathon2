'use client';

import { Bell, BellOff } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface NotificationBadgeProps {
  count?: number;
  hasUnread?: boolean;
  onOpen?: () => void;
  disabled?: boolean;
  className?: string;
}

export function NotificationBadge({
  count = 0,
  hasUnread = false,
  onOpen,
  disabled = false,
  className = ''
}: NotificationBadgeProps) {
  const hasNotifications = count > 0 || hasUnread;

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={onOpen}
      disabled={disabled}
      className={`relative ${className}`}
      aria-label={hasNotifications ? `You have ${count} notifications` : 'No notifications'}
    >
      {hasNotifications ? (
        <Bell className="h-5 w-5 text-primary" />
      ) : (
        <BellOff className="h-5 w-5 text-muted-foreground" />
      )}

      {hasNotifications && (
        <Badge
          variant="destructive"
          className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs"
        >
          {count > 9 ? '9+' : count}
        </Badge>
      )}
    </Button>
  );
}