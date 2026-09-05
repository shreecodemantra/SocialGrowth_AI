import { apiClient } from "./client";
import type { Campaign, CampaignCreateRequest, CampaignDetail } from "../types";

export async function listCampaigns(workspaceId: string): Promise<Campaign[]> {
  const { data } = await apiClient.get<Campaign[]>(`/workspaces/${workspaceId}/campaigns`);
  return data;
}

export async function getCampaign(workspaceId: string, campaignId: string): Promise<CampaignDetail> {
  const { data } = await apiClient.get<CampaignDetail>(`/workspaces/${workspaceId}/campaigns/${campaignId}`);
  return data;
}

export async function createCampaign(
  workspaceId: string,
  request: CampaignCreateRequest
): Promise<CampaignDetail> {
  const { data } = await apiClient.post<CampaignDetail>(`/workspaces/${workspaceId}/campaigns`, request);
  return data;
}

export async function deleteCampaign(workspaceId: string, campaignId: string): Promise<void> {
  await apiClient.delete(`/workspaces/${workspaceId}/campaigns/${campaignId}`);
}
