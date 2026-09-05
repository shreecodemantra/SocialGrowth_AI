import {
  AlertTriangle,
  Check,
  Facebook,
  Instagram,
  Linkedin,
  type LucideIcon,
  Pencil,
  RotateCw,
  X,
  Youtube,
} from "lucide-react";
import { useState } from "react";

import { approvePlatform, regeneratePlatform, rejectPlatform, updatePlatformContent } from "../api/posts";
import { extractErrorMessage } from "../api/client";
import type { PlatformContent, PlatformType, PostPlatform, PostStatus } from "../types";
import { Badge } from "./ui/Badge";
import { Button } from "./ui/Button";
import { Card, CardBody, CardHeader } from "./ui/Card";
import { Label } from "./ui/Input";
import { TagInput } from "./ui/TagInput";

const PLATFORM_META: Record<PlatformType, { label: string; icon: LucideIcon }> = {
  INSTAGRAM: { label: "Instagram", icon: Instagram },
  FACEBOOK: { label: "Facebook", icon: Facebook },
  LINKEDIN: { label: "LinkedIn", icon: Linkedin },
  YOUTUBE: { label: "YouTube", icon: Youtube },
};

const FIELD_CONFIG: Record<PlatformType, { key: keyof PlatformContent; label: string; multiline?: boolean }[]> = {
  INSTAGRAM: [
    { key: "hook", label: "Hook" },
    { key: "caption", label: "Caption", multiline: true },
    { key: "cta", label: "CTA" },
    { key: "reel_idea", label: "Reel Idea", multiline: true },
    { key: "alt_text", label: "Alt Text", multiline: true },
  ],
  LINKEDIN: [
    { key: "hook", label: "Hook" },
    { key: "post", label: "Post", multiline: true },
    { key: "cta", label: "CTA" },
  ],
  FACEBOOK: [
    { key: "post", label: "Post", multiline: true },
    { key: "cta", label: "CTA" },
  ],
  YOUTUBE: [
    { key: "video_title", label: "Video Title" },
    { key: "description", label: "Description", multiline: true },
    { key: "thumbnail_text", label: "Thumbnail Text" },
    { key: "shorts_script", label: "Shorts Script", multiline: true },
    { key: "longform_script", label: "Long-form Script", multiline: true },
  ],
};

const ARRAY_FIELDS: Record<PlatformType, { key: keyof PlatformContent; label: string }[]> = {
  INSTAGRAM: [{ key: "hashtags", label: "Hashtags" }],
  LINKEDIN: [{ key: "hashtags", label: "Hashtags" }],
  FACEBOOK: [{ key: "hashtags", label: "Hashtags" }],
  YOUTUBE: [
    { key: "tags", label: "Tags" },
    { key: "keywords", label: "Keywords" },
  ],
};

function statusTone(status: PostStatus): "brand" | "slate" | "green" | "amber" | "red" {
  switch (status) {
    case "APPROVED":
    case "PUBLISHED":
      return "green";
    case "PENDING_REVIEW":
    case "GENERATED":
      return "amber";
    case "CANCELLED":
    case "FAILED":
      return "red";
    case "SCHEDULED":
    case "PUBLISHING":
      return "brand";
    default:
      return "slate";
  }
}

export function PostPlatformCard({
  workspaceId,
  postId,
  platform,
  onUpdated,
}: {
  workspaceId: string;
  postId: string;
  platform: PostPlatform;
  onUpdated: (updated: PostPlatform) => void;
}) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState<PlatformContent>(platform.content);
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const meta = PLATFORM_META[platform.platform];
  const fields = FIELD_CONFIG[platform.platform];
  const arrayFields = ARRAY_FIELDS[platform.platform];
  const isFinal = platform.status === "PUBLISHED" || platform.status === "PUBLISHING";

  const run = async (key: string, action: () => Promise<PostPlatform>) => {
    setBusy(key);
    setError(null);
    try {
      const updated = await action();
      onUpdated(updated);
      if (key === "save") setEditing(false);
    } catch (err) {
      setError(extractErrorMessage(err, "That action failed."));
    } finally {
      setBusy(null);
    }
  };

  return (
    <Card>
      <CardHeader
        title={
          <span className="flex items-center gap-2">
            <meta.icon className="h-4 w-4 text-slate-500" />
            {meta.label}
          </span>
        }
        action={<Badge tone={statusTone(platform.status)}>{platform.status.replace("_", " ")}</Badge>}
      />
      <CardBody className="space-y-4">
        {platform.quality_violations.length > 0 && (
          <div className="flex items-start gap-2 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2.5 text-sm text-amber-800">
            <AlertTriangle className="mt-0.5 h-4 w-4 flex-none" />
            <ul className="list-inside list-disc">
              {platform.quality_violations.map((v) => (
                <li key={v}>{v}</li>
              ))}
            </ul>
          </div>
        )}

        {platform.primary_asset && (
          <img
            src={platform.primary_asset.storage_url}
            alt="Generated creative"
            className="w-full rounded-lg border border-slate-200 object-cover"
            style={{ aspectRatio: `${platform.primary_asset.width ?? 4} / ${platform.primary_asset.height ?? 5}` }}
          />
        )}

        {fields.map(({ key, label, multiline }) => (
          <div key={key}>
            <Label>{label}</Label>
            {editing ? (
              multiline ? (
                <textarea
                  value={(draft[key] as string) ?? ""}
                  onChange={(e) => setDraft({ ...draft, [key]: e.target.value })}
                  rows={3}
                  className="block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 shadow-xs focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
                />
              ) : (
                <input
                  value={(draft[key] as string) ?? ""}
                  onChange={(e) => setDraft({ ...draft, [key]: e.target.value })}
                  className="block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 shadow-xs focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
                />
              )
            ) : (
              <p className="whitespace-pre-wrap text-sm text-slate-700">{(platform.content[key] as string) || "—"}</p>
            )}
          </div>
        ))}

        {arrayFields.map(({ key, label }) => (
          <div key={key}>
            <Label>{label}</Label>
            {editing ? (
              <TagInput
                value={(draft[key] as string[]) ?? []}
                onChange={(v) => setDraft({ ...draft, [key]: v })}
              />
            ) : (
              <div className="flex flex-wrap gap-1.5">
                {((platform.content[key] as string[]) ?? []).map((tag) => (
                  <Badge key={tag} tone="brand">
                    {tag}
                  </Badge>
                ))}
              </div>
            )}
          </div>
        ))}

        {error && (
          <div className="flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2.5 text-sm text-red-700">
            <AlertTriangle className="mt-0.5 h-4 w-4 flex-none" />
            {error}
          </div>
        )}

        {!isFinal && (
          <div className="flex flex-wrap items-center gap-2 border-t border-slate-100 pt-4">
            {editing ? (
              <>
                <Button
                  size="sm"
                  icon={<Check className="h-4 w-4" />}
                  loading={busy === "save"}
                  onClick={() => run("save", () => updatePlatformContent(workspaceId, postId, platform.platform, draft))}
                >
                  Save
                </Button>
                <Button
                  size="sm"
                  variant="secondary"
                  icon={<X className="h-4 w-4" />}
                  onClick={() => {
                    setDraft(platform.content);
                    setEditing(false);
                  }}
                >
                  Cancel
                </Button>
              </>
            ) : (
              <>
                <Button
                  size="sm"
                  variant="secondary"
                  icon={<Pencil className="h-4 w-4" />}
                  onClick={() => {
                    setDraft(platform.content);
                    setEditing(true);
                  }}
                >
                  Edit
                </Button>
                <Button
                  size="sm"
                  variant="secondary"
                  icon={<RotateCw className="h-4 w-4" />}
                  loading={busy === "regenerate"}
                  onClick={() => run("regenerate", () => regeneratePlatform(workspaceId, postId, platform.platform))}
                >
                  Regenerate
                </Button>
                {platform.status !== "APPROVED" && (
                  <Button
                    size="sm"
                    icon={<Check className="h-4 w-4" />}
                    loading={busy === "approve"}
                    onClick={() => run("approve", () => approvePlatform(workspaceId, postId, platform.platform))}
                  >
                    Approve
                  </Button>
                )}
                {platform.status !== "CANCELLED" && (
                  <Button
                    size="sm"
                    variant="danger"
                    icon={<X className="h-4 w-4" />}
                    loading={busy === "reject"}
                    onClick={() => run("reject", () => rejectPlatform(workspaceId, postId, platform.platform))}
                  >
                    Reject
                  </Button>
                )}
              </>
            )}
          </div>
        )}
      </CardBody>
    </Card>
  );
}
