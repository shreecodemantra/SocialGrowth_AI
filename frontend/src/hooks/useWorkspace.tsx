import React, { createContext, useContext, useEffect, useState } from "react";

import { listWorkspaces } from "../api/workspaces";
import type { Workspace } from "../types";
import { useAuth } from "./useAuth";

interface WorkspaceContextValue {
  workspaces: Workspace[];
  currentWorkspace: Workspace | null;
  setCurrentWorkspace: (workspace: Workspace) => void;
  isLoading: boolean;
  refresh: () => Promise<void>;
}

const WorkspaceContext = createContext<WorkspaceContextValue | undefined>(undefined);

const LAST_WORKSPACE_KEY = "sga_last_workspace_id";

export function WorkspaceProvider({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [currentWorkspace, setCurrentWorkspaceState] = useState<Workspace | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const refresh = async () => {
    if (!isAuthenticated) {
      setWorkspaces([]);
      setCurrentWorkspaceState(null);
      setIsLoading(false);
      return;
    }
    setIsLoading(true);
    const list = await listWorkspaces();
    setWorkspaces(list);
    const lastId = localStorage.getItem(LAST_WORKSPACE_KEY);
    const restored = list.find((w) => w.id === lastId) ?? list[0] ?? null;
    setCurrentWorkspaceState(restored);
    setIsLoading(false);
  };

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated]);

  const setCurrentWorkspace = (workspace: Workspace) => {
    setCurrentWorkspaceState(workspace);
    localStorage.setItem(LAST_WORKSPACE_KEY, workspace.id);
  };

  return (
    <WorkspaceContext.Provider
      value={{ workspaces, currentWorkspace, setCurrentWorkspace, isLoading, refresh }}
    >
      {children}
    </WorkspaceContext.Provider>
  );
}

export function useWorkspace(): WorkspaceContextValue {
  const ctx = useContext(WorkspaceContext);
  if (!ctx) throw new Error("useWorkspace must be used within a WorkspaceProvider");
  return ctx;
}
