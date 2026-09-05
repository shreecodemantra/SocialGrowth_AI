import { Megaphone, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { deleteCampaign, listCampaigns } from "../../api/campaigns";
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
  const [deleteTarget, setDeleteTarget] = useState<Campaign | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  useEffect(() => {
    if (!currentWorkspace) return;
    setLoading(true);
    listCampaigns(currentWorkspace.id)
      .then(setCampaigns)
      .catch((err) => setError(extractErrorMessage(err)))
      .finally(() => setLoading(false));
  }, [currentWorkspace]);

  const handleDeleteConfirm = async () => {
    if (!deleteTarget || !currentWorkspace) return;
    setDeleting(true);
    setDeleteError(null);
    try {
      await deleteCampaign(currentWorkspace.id, deleteTarget.id);
      setCampaigns((prev) => prev.filter((c) => c.id !== deleteTarget.id));
      setDeleteTarget(null);
    } catch (err) {
      setDeleteError(extractErrorMessage(err));
    } finally {
      setDeleting(false);
    }
  };

  if (!currentWorkspace) {
    return <p className="text-sm text-slate-500">Create a workspace from the Dashboard first.</p>;
  }

  return (
    <div className="space-y-6">
      {/* ── Delete confirmation dialog ── */}
      {deleteTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
          <div className="w-full max-w-sm rounded-xl bg-white p-6 shadow-xl">
            <h2 className="text-base font-semibold text-slate-900">Delete campaign?</h2>
            <p className="mt-1.5 text-sm text-slate-500">
              <span className="font-medium text-slate-700">"{deleteTarget.title}"</span> and all its
              generated content will be permanently removed. This cannot be undone.
            </p>
            {deleteError && <p className="mt-3 text-sm text-red-600">{deleteError}</p>}
            <div className="mt-5 flex justify-end gap-3">
              <button
                onClick={() => { setDeleteTarget(null); setDeleteError(null); }}
                disabled={deleting}
                className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteConfirm}
                disabled={deleting}
                className="flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-700 disabled:opacity-50"
              >
                {deleting && <Spinner className="h-3.5 w-3.5" />}
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

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
          <div key={c.id} className="group flex items-stretch gap-2">
            {/* Campaign card — clicking navigates to detail */}
            <Link to={`/campaigns/${c.id}`} className="min-w-0 flex-1">
              <Card className="h-full p-4 transition-shadow hover:shadow-card-hover">
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
            {/* Delete button — separate from Link so it never triggers navigation */}
            <button
              onClick={() => setDeleteTarget(c)}
              title="Delete campaign"
              className="flex-shrink-0 self-center rounded-lg border border-transparent p-2 text-slate-300 opacity-0 transition-all hover:border-red-200 hover:bg-red-50 hover:text-red-600 group-hover:opacity-100"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
