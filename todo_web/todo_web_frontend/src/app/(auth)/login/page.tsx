import { LoginForm } from '@/components/auth/login-form';
import { Card } from '@/components/ui/card';

export const metadata = {
  title: 'Sign In - Todo App',
  description: 'Sign in to your account to manage your tasks',
};

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Welcome Back</h1>
          <p className="text-gray-600 mt-2">Sign in to your account to continue</p>
        </div>

        <Card className="shadow-lg">
          <LoginForm />
        </Card>
      </div>
    </div>
  );
}
