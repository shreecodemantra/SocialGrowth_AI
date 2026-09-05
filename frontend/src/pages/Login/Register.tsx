import { AlertCircle, Lock, Mail, User } from "lucide-react";
import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { extractErrorMessage } from "../../api/client";
import { Button } from "../../components/ui/Button";
import { HelperText, Input, Label } from "../../components/ui/Input";
import { useAuth } from "../../hooks/useAuth";
import { AuthLayout } from "./AuthLayout";

export function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await register(email, password, fullName);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(extractErrorMessage(err, "Could not create your account."));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AuthLayout title="Create your account" subtitle="Start automating your social content in minutes.">
      <form className="space-y-4" onSubmit={handleSubmit}>
        <div>
          <Label>Full name</Label>
          <Input
            autoFocus
            icon={<User className="h-4 w-4" />}
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder="Jordan Lee"
          />
        </div>
        <div>
          <Label>Email</Label>
          <Input
            type="email"
            required
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
            minLength={8}
            icon={<Lock className="h-4 w-4" />}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
          />
          <HelperText>At least 8 characters.</HelperText>
        </div>

        {error && (
          <div className="flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2.5 text-sm text-red-700">
            <AlertCircle className="mt-0.5 h-4 w-4 flex-none" />
            {error}
          </div>
        )}

        <Button type="submit" size="lg" loading={submitting} className="w-full">
          {submitting ? "Creating account..." : "Create account"}
        </Button>
      </form>

      <p className="mt-6 text-center text-sm text-slate-500">
        Already have an account?{" "}
        <Link to="/login" className="font-semibold text-brand-600 hover:text-brand-700">
          Sign in
        </Link>
      </p>
    </AuthLayout>
  );
}
