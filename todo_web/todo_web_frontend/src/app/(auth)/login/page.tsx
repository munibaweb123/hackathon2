import { LoginForm } from '@/components/auth/login-form';

export const metadata = {
  title: 'Sign In - Todo App',
  description: 'Sign in to your account to manage your tasks',
};

export default function LoginPage() {
  return <LoginForm />;
}
