import { AlertCircle, Lock, Mail } from "lucide-react";
import React, { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { extractErrorMessage } from "../../api/client";
import { Button } from "../../components/ui/Button";
import { Input, Label } from "../../components/ui/Input";
import { useAuth } from "../../hooks/useAuth";
import { AuthLayout } from "./AuthLayout";

export function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await login(email, password);
      const redirectTo = (location.state as { from?: string })?.from || "/dashboard";
      navigate(redirectTo, { replace: true });
    } catch (err) {
      setError(extractErrorMessage(err, "Invalid email or password."));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AuthLayout title="Welcome back" subtitle="Sign in to your workspace to continue.">
      <form className="space-y-4" onSubmit={handleSubmit}>
        <div>
          <Label>Email</Label>
          <Input
            type="email"
            required
            autoFocus
            icon={<Mail className="h-4 w-4" />}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@company.com"
          />
        </div>
        <div>
          <Label>Password</Label>
          <Input
            type="password"
            required
            icon={<Lock className="h-4 w-4" />}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
          />
        </div>

        {error && (
          <div className="flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2.5 text-sm text-red-700">
            <AlertCircle className="mt-0.5 h-4 w-4 flex-none" />
            {error}
          </div>
        )}

        <Button type="submit" size="lg" loading={submitting} className="w-full">
          {submitting ? "Signing in..." : "Sign in"}
        </Button>
      </form>

      <p className="mt-6 text-center text-sm text-slate-500">
        Don&apos;t have an account?{" "}
        <Link to="/register" className="font-semibold text-brand-600 hover:text-brand-700">
          Create one
        </Link>
      </p>
    </AuthLayout>
  );
}
