import { Megaphone } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { listCampaigns } from "../../api/campaigns";
import { extractErrorMessage } from "../../api/client";
import { Badge } from "../../components/ui/Badge";
import { Card } from "../../components/ui/Card";
import { EmptyState } from "../../components/ui/EmptyState";
import { Spinner } from "../../components/ui/Spinner";
import { useWorkspace } from "../../hooks/useWorkspace";
import type { Campaign, CampaignStatus } from "../../types";

function statusTone(status: CampaignStatus): "brand" | "slate" | "green" | "amber" | "red" {
  switch (status) {
    case "READY":
      return "green";
    case "GENERATING":
      return "amber";
    case "FAILED":
      return "red";
    default:
      return "slate";
  }
}

export function Campaigns() {
  const { currentWorkspace } = useWorkspace();
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!currentWorkspace) return;
    setLoading(true);
    listCampaigns(currentWorkspace.id)
      .then(setCampaigns)
      .catch((err) => setError(extractErrorMessage(err)))
      .finally(() => setLoading(false));
  }, [currentWorkspace]);

  if (!currentWorkspace) {
    return <p className="text-sm text-slate-500">Create a workspace from the Dashboard first.</p>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Campaigns</h1>
          <p className="mt-1 text-sm text-slate-500">Every topic you've generated content for.</p>
        </div>
        <Link
          to="/content-generator"
          className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-700"
        >
          New Campaign
        </Link>
      </div>

      {loading && (
        <div className="flex items-center gap-2 py-12 text-sm text-slate-400">
          <Spinner className="h-4 w-4" />
          Loading campaigns...
        </div>
      )}

      {error && <p className="text-sm text-red-600">{error}</p>}

      {!loading && campaigns.length === 0 && (
        <EmptyState
          icon={<Megaphone className="h-6 w-6" />}
          title="No campaigns yet"
          description="Create your first campaign from the Content Generator to see it here."
        />
      )}

      <div className="space-y-3">
        {campaigns.map((c) => (
          <Link key={c.id} to={`/campaigns/${c.id}`}>
            <Card className="p-4 transition-shadow hover:shadow-card-hover">
              <div className="flex items-center justify-between gap-4">
                <div className="min-w-0">
                  <h3 className="truncate text-sm font-semibold text-slate-900">{c.title}</h3>
                  <div className="mt-1.5 flex flex-wrap gap-1.5">
                    {c.platforms.map((p) => (
                      <Badge key={p} tone="slate">
                        {p}
                      </Badge>
                    ))}
                  </div>
                </div>
                <Badge tone={statusTone(c.status)}>{c.status}</Badge>
              </div>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
