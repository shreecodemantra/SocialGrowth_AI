import React from "react";
import { Navigate } from "react-router-dom";

import { useAuth } from "../hooks/useAuth";
import { FullPageSpinner } from "./ui/Spinner";

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <FullPageSpinner label="Loading your workspace..." />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}
