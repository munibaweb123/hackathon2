'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckSquare, Bell, Settings, LogOut, User, Menu, X, MessageSquare } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { ThemeToggle } from '@/components/theme-toggle';
import { useAuth } from '@/hooks/use-auth';
import { cn } from '@/lib/utils';

const navItems = [
  { href: '/tasks', label: 'Tasks', icon: CheckSquare },
  { href: '/chat', label: 'AI Assistant', icon: MessageSquare },
  { href: '/reminders', label: 'Reminders', icon: Bell },
  { href: '/preferences', label: 'Preferences', icon: Settings },
];

export function Header() {
  const { user, logout, isLoading } = useAuth();
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const initials = user?.name
    ? user.name
        .split(' ')
        .map((n) => n[0])
        .join('')
        .toUpperCase()
    : user?.email?.[0]?.toUpperCase() || '?';

  return (
    <>
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="sticky top-0 z-50 w-full border-b bg-background/80 backdrop-blur-lg supports-[backdrop-filter]:bg-background/60"
    >
      <div className="container flex h-16 items-center px-4 sm:px-6">
        <Link href="/tasks" className="flex items-center space-x-2 group">
          <motion.div
            whileHover={{ rotate: 5, scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="flex items-center justify-center w-9 h-9 rounded-lg bg-primary text-primary-foreground"
          >
            <CheckSquare className="h-5 w-5" />
          </motion.div>
          <span className="font-bold text-lg hidden sm:inline-block group-hover:text-primary transition-colors">
            TaskFlow
          </span>
        </Link>

        <div className="flex-1" />

        <div className="flex items-center gap-2">
          {/* Mobile menu toggle */}
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle mobile menu"
          >
            {mobileMenuOpen ? (
              <X className="h-5 w-5" />
            ) : (
              <Menu className="h-5 w-5" />
            )}
          </Button>

          <ThemeToggle />

          {user && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="relative h-9 w-9 rounded-full ring-2 ring-transparent hover:ring-primary/20 transition-all">
                  <Avatar className="h-9 w-9">
                    <AvatarImage src={user.image} alt={user.name || user.email} />
                    <AvatarFallback className="bg-primary/10 text-primary font-semibold">
                      {initials}
                    </AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-56" align="end" forceMount>
                <DropdownMenuLabel className="font-normal">
                  <div className="flex flex-col space-y-1">
                    {user.name && (
                      <p className="text-sm font-medium leading-none">{user.name}</p>
                    )}
                    <p className="text-xs leading-none text-muted-foreground">
                      {user.email}
                    </p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem asChild>
                  <Link href="/profile" className="flex items-center cursor-pointer">
                    <User className="mr-2 h-4 w-4" />
                    Profile
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/tasks" className="flex items-center cursor-pointer">
                    <CheckSquare className="mr-2 h-4 w-4" />
                    My Tasks
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/reminders" className="flex items-center cursor-pointer">
                    <Bell className="mr-2 h-4 w-4" />
                    Reminders
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/preferences" className="flex items-center cursor-pointer">
                    <Settings className="mr-2 h-4 w-4" />
                    Preferences
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  onClick={logout}
                  disabled={isLoading}
                  className="cursor-pointer text-destructive focus:text-destructive"
                >
                  <LogOut className="mr-2 h-4 w-4" />
                  {isLoading ? 'Signing out...' : 'Sign out'}
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </div>
      </div>
    </motion.header>

      {/* Mobile Navigation Menu */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="md:hidden border-b bg-background overflow-hidden"
          >
            <nav className="container px-4 py-4 space-y-2">
              {navItems.map((item) => {
                const isActive = pathname === item.href;
                const Icon = item.icon;

                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={cn(
                      'flex items-center gap-3 px-4 py-3 rounded-lg transition-all',
                      isActive
                        ? 'bg-primary/10 text-primary font-medium'
                        : 'hover:bg-muted text-muted-foreground hover:text-foreground'
                    )}
                  >
                    <Icon className="h-5 w-5" />
                    {item.label}
                    {isActive && (
                      <motion.div
                        layoutId="mobileActiveIndicator"
                        className="ml-auto w-2 h-2 rounded-full bg-primary"
                        transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                      />
                    )}
                  </Link>
                );
              })}

              {/* Mobile user actions */}
              {user && (
                <>
                  <div className="pt-2 mt-2 border-t space-y-2">
                    <Link
                      href="/profile"
                      onClick={() => setMobileMenuOpen(false)}
                      className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-muted transition-all text-muted-foreground hover:text-foreground"
                    >
                      <User className="h-5 w-5" />
                      Profile
                    </Link>
                    <button
                      onClick={() => {
                        setMobileMenuOpen(false);
                        logout();
                      }}
                      disabled={isLoading}
                      className="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-destructive/10 transition-all text-destructive disabled:opacity-50"
                    >
                      <LogOut className="h-5 w-5" />
                      {isLoading ? 'Signing out...' : 'Sign out'}
                    </button>
                  </div>
                </>
              )}
            </nav>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
