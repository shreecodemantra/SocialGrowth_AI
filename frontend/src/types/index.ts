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
