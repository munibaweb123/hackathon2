import { RegisterForm } from '@/components/auth/register-form';

export const metadata = {
  title: 'Create Account - Todo App',
  description: 'Create a new account to start managing your tasks',
};

export default function RegisterPage() {
  return <RegisterForm />;
}
