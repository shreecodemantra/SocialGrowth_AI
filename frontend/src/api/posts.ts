import { apiClient } from "./client";
import type { PlatformContent, PlatformType, Post, PostPlatform } from "../types";

export async function listPosts(workspaceId: string): Promise<Post[]> {
  const { data } = await apiClient.get<Post[]>(`/workspaces/${workspaceId}/posts`);
  return data;
}

export async function getPost(workspaceId: string, postId: string): Promise<Post> {
  const { data } = await apiClient.get<Post>(`/workspaces/${workspaceId}/posts/${postId}`);
  return data;
}

export async function approvePlatform(
  workspaceId: string,
  postId: string,
  platform: PlatformType
): Promise<PostPlatform> {
  const { data } = await apiClient.post<PostPlatform>(
    `/workspaces/${workspaceId}/posts/${postId}/platforms/${platform}/approve`
  );
  return data;
}

export async function rejectPlatform(
  workspaceId: string,
  postId: string,
  platform: PlatformType
): Promise<PostPlatform> {
  const { data } = await apiClient.post<PostPlatform>(
    `/workspaces/${workspaceId}/posts/${postId}/platforms/${platform}/reject`
  );
  return data;
}

export async function updatePlatformContent(
  workspaceId: string,
  postId: string,
  platform: PlatformType,
  content: PlatformContent
): Promise<PostPlatform> {
  const { data } = await apiClient.patch<PostPlatform>(
    `/workspaces/${workspaceId}/posts/${postId}/platforms/${platform}`,
    { content }
  );
  return data;
}

export async function regeneratePlatform(
  workspaceId: string,
  postId: string,
  platform: PlatformType
): Promise<PostPlatform> {
  const { data } = await apiClient.post<PostPlatform>(
    `/workspaces/${workspaceId}/posts/${postId}/platforms/${platform}/regenerate`
  );
  return data;
}
