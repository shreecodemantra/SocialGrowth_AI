export interface User {
  id: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
}

export interface Workspace {
  id: string;
  name: string;
  slug: string;
  owner_id: string;
}

export type WorkspaceRole = "OWNER" | "ADMIN" | "EDITOR" | "VIEWER";

export interface WorkspaceMember {
  id: string;
  user_id: string;
  workspace_id: string;
  role: WorkspaceRole;
}

export interface BrandProfile {
  id?: string;
  workspace_id?: string;
  brand_name: string;
  description: string | null;
  website: string | null;
  industry: string | null;
  target_audience: string[];
  target_countries: string[];
  target_languages: string[];
  brand_tone: string | null;
  brand_keywords: string[];
  forbidden_words: string[];
  cta_style: string | null;
  preferred_hashtags: string[];
  logo_url: string | null;
  brand_colors: string[];
}

export interface ApiErrorPayload {
  success: false;
  error: {
    code: string;
    message: string;
    retryable: boolean;
  };
}

export type PlatformType = "INSTAGRAM" | "FACEBOOK" | "LINKEDIN" | "YOUTUBE";

export type PostStatus =
  | "DRAFT"
  | "GENERATING"
  | "GENERATED"
  | "PENDING_REVIEW"
  | "APPROVED"
  | "SCHEDULED"
  | "PUBLISHING"
  | "PUBLISHED"
  | "FAILED"
  | "CANCELLED";

export type CampaignStatus = "DRAFT" | "GENERATING" | "READY" | "FAILED";

export interface Asset {
  id: string;
  asset_type: string;
  storage_url: string;
  width: number | null;
  height: number | null;
  content_type: string;
}

// Per-platform content shapes (spec section 5) — every field is optional on
// the frontend type since each platform only fills in its own subset.
export interface PlatformContent {
  // Instagram
  caption?: string;
  hook?: string;
  reel_idea?: string;
  alt_text?: string;
  // Instagram / LinkedIn / Facebook
  cta?: string;
  hashtags?: string[];
  image_prompt?: string;
  // LinkedIn / Facebook
  post?: string;
  // YouTube
  video_title?: string;
  description?: string;
  tags?: string[];
  keywords?: string[];
  thumbnail_text?: string;
  thumbnail_prompt?: string;
  shorts_script?: string;
  longform_script?: string;
}

export interface PostPlatform {
  id: string;
  platform: PlatformType;
  content: PlatformContent;
  status: PostStatus;
  quality_violations: string[];
  external_post_id: string | null;
  primary_asset: Asset | null;
}

export interface StatusHistoryEntry {
  status: PostStatus;
  note: string | null;
  created_at: string;
}

export interface Post {
  id: string;
  display_id: string;
  title: string;
  status: PostStatus;
  content_score: number | null;
  campaign_id: string;
  platforms: PostPlatform[];
  status_history: StatusHistoryEntry[];
}

export interface Campaign {
  id: string;
  title: string;
  goal: string | null;
  platforms: PlatformType[];
  generate_images: boolean;
  generate_video: boolean;
  status: CampaignStatus;
  failure_reason: string | null;
  created_at: string;
}

export interface CampaignDetail extends Campaign {
  posts: Post[];
}

export interface CampaignCreateRequest {
  title: string;
  goal?: string;
  target_audience?: string[];
  platforms: PlatformType[];
  generate_images: boolean;
  generate_video: boolean;
}
