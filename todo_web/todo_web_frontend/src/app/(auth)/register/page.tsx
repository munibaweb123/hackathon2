import { RegisterForm } from '@/components/auth/register-form';
import { Card } from '@/components/ui/card';

export const metadata = {
  title: 'Create Account - Todo App',
  description: 'Create a new account to start managing your tasks',
};

export default function RegisterPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Welcome to Todo App</h1>
          <p className="text-gray-600 mt-2">Create your account to get started</p>
        </div>

        <Card className="shadow-lg">
          <RegisterForm />
        </Card>
      </div>
    </div>
  );
}
