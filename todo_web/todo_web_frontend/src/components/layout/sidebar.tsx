'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import { CheckSquare, Bell, Settings, LayoutDashboard } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

const navItems = [
  { href: '/tasks', label: 'Tasks', icon: CheckSquare },
  { href: '/reminders', label: 'Reminders', icon: Bell },
  { href: '/preferences', label: 'Preferences', icon: Settings },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { x: -20, opacity: 0 },
  visible: {
    x: 0,
    opacity: 1,
    transition: {
      type: 'spring' as const,
      stiffness: 300,
      damping: 24,
    },
  },
};

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 border-r bg-sidebar hidden md:flex md:flex-col">
      <div className="flex flex-col h-full">
        {/* Logo area */}
        <div className="h-16 flex items-center px-6 border-b">
          <Link href="/tasks" className="flex items-center space-x-2 group">
            <motion.div
              whileHover={{ rotate: 5, scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="flex items-center justify-center w-8 h-8 rounded-lg bg-primary text-primary-foreground"
            >
              <CheckSquare className="h-4 w-4" />
            </motion.div>
            <span className="font-bold text-lg">TaskFlow</span>
          </Link>
        </div>

        {/* Navigation */}
        <motion.nav
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="flex-1 px-3 py-4 space-y-1"
        >
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;

            return (
              <motion.div key={item.href} variants={itemVariants}>
                <Button
                  variant={isActive ? 'secondary' : 'ghost'}
                  className={cn(
                    'w-full justify-start gap-3 h-11 px-3 font-medium transition-all',
                    isActive && 'bg-primary/10 text-primary hover:bg-primary/15 hover:text-primary',
                    !isActive && 'hover:bg-muted'
                  )}
                  asChild
                >
                  <Link href={item.href}>
                    <Icon className={cn('h-5 w-5', isActive && 'text-primary')} />
                    {item.label}
                    {isActive && (
                      <motion.div
                        layoutId="activeIndicator"
                        className="ml-auto w-1.5 h-1.5 rounded-full bg-primary"
                        transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                      />
                    )}
                  </Link>
                </Button>
              </motion.div>
            );
          })}
        </motion.nav>

        {/* Footer area */}
        <div className="p-4 border-t">
          <div className="rounded-lg bg-primary/5 p-4">
            <p className="text-sm font-medium text-primary">Stay Productive</p>
            <p className="text-xs text-muted-foreground mt-1">
              Organize your tasks and never miss a deadline.
            </p>
          </div>
        </div>
      </div>
    </aside>
  );
}
