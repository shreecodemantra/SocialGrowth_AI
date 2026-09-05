import { apiClient } from "./client";
import type { BrandProfile, Workspace } from "../types";

export async function listWorkspaces(): Promise<Workspace[]> {
  const { data } = await apiClient.get<Workspace[]>("/workspaces");
  return data;
}

export async function createWorkspace(name: string): Promise<Workspace> {
  const { data } = await apiClient.post<Workspace>("/workspaces", { name });
  return data;
}

export async function getBrandProfile(workspaceId: string): Promise<BrandProfile | null> {
  const { data } = await apiClient.get<BrandProfile | null>(`/workspaces/${workspaceId}/brand`);
  return data;
}

export async function saveBrandProfile(workspaceId: string, profile: BrandProfile): Promise<BrandProfile> {
  const { data } = await apiClient.put<BrandProfile>(`/workspaces/${workspaceId}/brand`, profile);
  return data;
}
