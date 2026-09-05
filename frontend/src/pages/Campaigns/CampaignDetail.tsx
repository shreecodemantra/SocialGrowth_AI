import { ArrowLeft } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { getCampaign } from "../../api/campaigns";
import { extractErrorMessage } from "../../api/client";
import { PostPlatformCard } from "../../components/PostPlatformCard";
import { Badge } from "../../components/ui/Badge";
import { Spinner } from "../../components/ui/Spinner";
import { useWorkspace } from "../../hooks/useWorkspace";
import type { CampaignDetail as CampaignDetailType, PostPlatform } from "../../types";

export function CampaignDetail() {
  const { currentWorkspace } = useWorkspace();
  const { campaignId } = useParams<{ campaignId: string }>();
  const [campaign, setCampaign] = useState<CampaignDetailType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!currentWorkspace || !campaignId) return;
    setLoading(true);
    getCampaign(currentWorkspace.id, campaignId)
      .then(setCampaign)
      .catch((err) => setError(extractErrorMessage(err)))
      .finally(() => setLoading(false));
  }, [currentWorkspace, campaignId]);

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

  if (loading) {
    return (
      <div className="flex items-center gap-2 py-12 text-sm text-slate-400">
        <Spinner className="h-4 w-4" />
        Loading campaign...
      </div>
    );
  }
  if (error) return <p className="text-sm text-red-600">{error}</p>;
  if (!campaign) return null;

  return (
    <div className="space-y-6">
      <Link to="/campaigns" className="flex items-center gap-1.5 text-sm font-medium text-slate-500 hover:text-slate-800">
        <ArrowLeft className="h-4 w-4" />
        Back to Campaigns
      </Link>

      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">{campaign.title}</h1>
        <p className="mt-1 text-sm text-slate-500">{campaign.goal}</p>
      </div>

      {campaign.posts.map((post) => (
        <div key={post.id} className="space-y-3">
          <div className="flex items-center gap-3">
            <h2 className="text-sm font-semibold text-slate-500">{post.display_id}</h2>
            <Badge tone="slate">{post.status.replace("_", " ")}</Badge>
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            {post.platforms.map((pp) => (
              <PostPlatformCard
                key={pp.id}
                workspaceId={currentWorkspace!.id}
                postId={post.id}
                platform={pp}
                onUpdated={updatePlatformInState}
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
