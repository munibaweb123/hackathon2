'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

export function Sidebar() {
  const pathname = usePathname();

  const navItems = [
    { href: '/tasks', label: 'Tasks', icon: '📋' },
    { href: '/reminders', label: 'Reminders', icon: '⏰' },
    { href: '/preferences', label: 'Preferences', icon: '⚙️' },
  ];

  return (
    <aside className="w-64 border-r bg-muted/40 hidden md:block">
      <div className="p-4">
        <h2 className="text-lg font-semibold mb-4">Todo App</h2>
        <nav className="space-y-1">
          {navItems.map((item) => (
            <Button
              key={item.href}
              variant={pathname === item.href ? 'secondary' : 'ghost'}
              className={cn(
                'w-full justify-start',
                pathname === item.href && 'bg-background'
              )}
              asChild
            >
              <Link href={item.href}>
                <span className="mr-2">{item.icon}</span>
                {item.label}
              </Link>
            </Button>
          ))}
        </nav>
      </div>
    </aside>
  );
}