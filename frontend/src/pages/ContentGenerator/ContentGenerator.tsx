import {
  AlertCircle,
  Facebook,
  Instagram,
  Linkedin,
  type LucideIcon,
  Sparkles,
  Youtube,
} from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";

import { createCampaign } from "../../api/campaigns";
import { extractErrorMessage } from "../../api/client";
import { PostPlatformCard } from "../../components/PostPlatformCard";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { Card, CardBody, CardHeader } from "../../components/ui/Card";
import { HelperText, Input, Label } from "../../components/ui/Input";
import { Spinner } from "../../components/ui/Spinner";
import { useWorkspace } from "../../hooks/useWorkspace";
import type { CampaignDetail, PlatformType, PostPlatform } from "../../types";

const PLATFORM_OPTIONS: { value: PlatformType; label: string; icon: LucideIcon }[] = [
  { value: "INSTAGRAM", label: "Instagram", icon: Instagram },
  { value: "LINKEDIN", label: "LinkedIn", icon: Linkedin },
  { value: "FACEBOOK", label: "Facebook", icon: Facebook },
  { value: "YOUTUBE", label: "YouTube", icon: Youtube },
];

export function ContentGenerator() {
  const { currentWorkspace } = useWorkspace();
  const [title, setTitle] = useState("");
  const [goal, setGoal] = useState("Brand Awareness");
  const [platforms, setPlatforms] = useState<PlatformType[]>(["INSTAGRAM", "LINKEDIN"]);
  const [generateImages, setGenerateImages] = useState(true);
  const [generateVideo, setGenerateVideo] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [campaign, setCampaign] = useState<CampaignDetail | null>(null);

  if (!currentWorkspace) {
    return <p className="text-sm text-slate-500">Create a workspace from the Dashboard first.</p>;
  }

  const togglePlatform = (value: PlatformType) => {
    setPlatforms((prev) => (prev.includes(value) ? prev.filter((p) => p !== value) : [...prev, value]));
  };

  const handleGenerate = async () => {
    setSubmitting(true);
    setError(null);
    try {
      const result = await createCampaign(currentWorkspace.id, {
        title,
        goal: goal || undefined,
        platforms,
        generate_images: generateImages,
        generate_video: generateVideo,
      });
      setCampaign(result);
    } catch (err) {
      setError(extractErrorMessage(err, "Content generation failed."));
    } finally {
      setSubmitting(false);
    }
  };

  const updatePlatformInState = (updated: PostPlatform) => {
    setCampaign((prev) =>
      prev
        ? {
            ...prev,
            posts: prev.posts.map((post) => ({
              ...post,
              platforms: post.platforms.map((p) => (p.id === updated.id ? updated : p)),
            })),
          }
        : prev
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Content Generator</h1>
        <p className="mt-1 text-sm text-slate-500">
          Enter one idea — the pipeline researches it, then writes dedicated content per platform.
        </p>
      </div>

      {!campaign && (
        <Card className="max-w-2xl">
          <CardHeader title="Create Campaign" />
          <CardBody className="space-y-5">
            <div>
              <Label>Topic / title</Label>
              <Input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Transforming Students into Industry-Ready Developers"
              />
            </div>
            <div>
              <Label>Goal</Label>
              <Input value={goal} onChange={(e) => setGoal(e.target.value)} placeholder="Brand Awareness" />
            </div>

            <div>
              <Label>Platforms</Label>
              <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
                {PLATFORM_OPTIONS.map((opt) => {
                  const active = platforms.includes(opt.value);
                  return (
                    <button
                      key={opt.value}
                      type="button"
                      onClick={() => togglePlatform(opt.value)}
                      className={[
                        "flex flex-col items-center gap-1.5 rounded-lg border px-3 py-3 text-xs font-medium transition-colors",
                        active
                          ? "border-brand-300 bg-brand-50 text-brand-700"
                          : "border-slate-200 text-slate-500 hover:border-slate-300",
                      ].join(" ")}
                    >
                      <opt.icon className="h-5 w-5" />
                      {opt.label}
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="space-y-2.5">
              <label className="flex items-center gap-2.5 text-sm text-slate-700">
                <input
                  type="checkbox"
                  checked={generateImages}
                  onChange={(e) => setGenerateImages(e.target.checked)}
                  className="h-4 w-4 rounded border-slate-300 text-brand-600 focus:ring-brand-500"
                />
                Generate images
              </label>
              <label className="flex items-center gap-2.5 text-sm text-slate-700">
                <input
                  type="checkbox"
                  checked={generateVideo}
                  onChange={(e) => setGenerateVideo(e.target.checked)}
                  className="h-4 w-4 rounded border-slate-300 text-brand-600 focus:ring-brand-500"
                />
                Generate video (Reel / Short)
              </label>
              {generateVideo && (
                <HelperText>
                  Video generation calls a paid, metered API and can take several minutes to respond.
                </HelperText>
              )}
            </div>

            {error && (
              <div className="flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2.5 text-sm text-red-700">
                <AlertCircle className="mt-0.5 h-4 w-4 flex-none" />
                <span>
                  {error}
                  {error.toLowerCase().includes("brand profile") && (
                    <>
                      {" "}
                      <Link to="/brand-settings" className="font-semibold underline">
                        Set it up now
                      </Link>
                    </>
                  )}
                </span>
              </div>
            )}

            <Button
              icon={<Sparkles className="h-4 w-4" />}
              loading={submitting}
              disabled={!title.trim() || platforms.length === 0}
              onClick={handleGenerate}
              className="w-full"
            >
              {submitting ? "Generating campaign..." : "Generate Campaign"}
            </Button>
            {submitting && (
              <p className="flex items-center justify-center gap-2 text-xs text-slate-400">
                <Spinner className="h-3.5 w-3.5" />
                Researching, writing, and generating creatives — this can take up to a minute.
              </p>
            )}
          </CardBody>
        </Card>
      )}

      {campaign && (
        <div className="space-y-6">
          {campaign.status === "FAILED" && (
            <div className="flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2.5 text-sm text-red-700">
              <AlertCircle className="mt-0.5 h-4 w-4 flex-none" />
              Generation failed: {campaign.failure_reason}
            </div>
          )}

          {campaign.posts.map((post) => (
            <div key={post.id} className="space-y-3">
              <div className="flex items-center gap-3">
                <h2 className="text-sm font-semibold text-slate-500">{post.display_id}</h2>
                <Badge tone="slate">{post.status.replace("_", " ")}</Badge>
              </div>
              <h3 className="text-lg font-bold text-slate-900">{post.title}</h3>

              <div className="grid gap-4 lg:grid-cols-2">
                {post.platforms.map((pp) => (
                  <PostPlatformCard
                    key={pp.id}
                    workspaceId={currentWorkspace.id}
                    postId={post.id}
                    platform={pp}
                    onUpdated={updatePlatformInState}
                  />
                ))}
              </div>
            </div>
          ))}

          <Button variant="secondary" onClick={() => setCampaign(null)}>
            Create another campaign
          </Button>
        </div>
      )}
    </div>
  );
}
