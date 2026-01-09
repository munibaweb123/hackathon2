'use client';

import { toast as sonnerToast } from 'sonner';

export interface ToastProps {
  title?: string;
  description?: string;
  variant?: 'default' | 'destructive';
  duration?: number;
}

export function useToast() {
  const toast = ({ title, description, variant, duration }: ToastProps) => {
    const message = title || '';
    const options = {
      description,
      duration,
    };

    if (variant === 'destructive') {
      sonnerToast.error(message, options);
    } else {
      sonnerToast.success(message, options);
    }
  };

  return { toast };
}
