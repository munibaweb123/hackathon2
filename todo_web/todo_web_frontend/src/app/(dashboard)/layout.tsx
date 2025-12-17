'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Header } from '@/components/layout/header';
import { Sidebar } from '@/components/layout/sidebar';
import { Footer } from '@/components/layout/footer';
import { useAuth } from '@/hooks/use-auth';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isAuthenticated, isLoading, user, error } = useAuth();
  const router = useRouter();
  const [shouldRedirect, setShouldRedirect] = useState(false);

  // Debug logging
  useEffect(() => {
    console.log('[DashboardLayout] Auth state:', {
      isAuthenticated,
      isLoading,
      user: user ? { id: user.id, email: user.email } : null,
      error: error?.message || null,
    });
  }, [isAuthenticated, isLoading, user, error]);

  // Handle redirect after loading completes
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      console.log('[DashboardLayout] Not authenticated after loading, will redirect...');
      // Add delay before redirecting to avoid race condition
      const timer = setTimeout(() => {
        if (!isAuthenticated) {
          console.log('[DashboardLayout] Redirecting to login...');
          setShouldRedirect(true);
          router.push('/login');
        }
      }, 2000); // Wait 2 seconds before redirecting

      return () => clearTimeout(timer);
    }
  }, [isAuthenticated, isLoading, router]);

  // Show loading state
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="flex flex-col items-center gap-4"
        >
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}
            className="w-10 h-10 border-3 border-primary border-t-transparent rounded-full"
          />
          <p className="text-muted-foreground text-sm">Loading...</p>
        </motion.div>
      </div>
    );
  }

  // If not authenticated and should redirect, show loading
  if (!isAuthenticated && !shouldRedirect) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="flex flex-col items-center gap-4"
        >
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}
            className="w-10 h-10 border-3 border-primary border-t-transparent rounded-full"
          />
          <p className="text-muted-foreground text-sm">Verifying session...</p>
        </motion.div>
      </div>
    );
  }

  // If redirecting, show nothing
  if (shouldRedirect) {
    return null;
  }

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <div className="flex flex-1">
        <Sidebar />
        <div className="flex-1 flex flex-col min-w-0">
          <Header />
          <AnimatePresence mode="wait">
            <motion.main
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="flex-1 container px-4 sm:px-6 py-6 max-w-6xl"
            >
              {children}
            </motion.main>
          </AnimatePresence>
          <Footer />
        </div>
      </div>
    </div>
  );
}
