'use client';

import { ProfileForm } from '@/components/auth/profile-form';
import { motion } from 'framer-motion';

export default function ProfilePage() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col items-center justify-center py-8"
    >
      <ProfileForm />
    </motion.div>
  );
}
