import {
  AlertCircle,
  BarChart3,
  Eye,
  Heart,
  LayoutDashboard,
  type LucideIcon,
  PlayCircle,
  Radar,
  Trophy,
  UserPlus,
} from "lucide-react";
import { useState } from "react";

import { extractErrorMessage } from "../../api/client";
import { createWorkspace } from "../../api/workspaces";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { EmptyState } from "../../components/ui/EmptyState";
import { HelperText, Input, Label } from "../../components/ui/Input";
import { useWorkspace } from "../../hooks/useWorkspace";

interface StatCard {
  label: string;
  icon: LucideIcon;
}

const STAT_CARDS: StatCard[] = [
  { label: "Total Posts", icon: BarChart3 },
  { label: "Total Reach", icon: Radar },
  { label: "Total Impressions", icon: Eye },
  { label: "Total Engagements", icon: Heart },
  { label: "Total Views", icon: PlayCircle },
  { label: "Avg. Engagement Rate", icon: BarChart3 },
  { label: "Followers Growth", icon: UserPlus },
  { label: "Best Platform", icon: Trophy },
];

export function Dashboard() {
  const { workspaces, currentWorkspace, refresh } = useWorkspace();
  const [name, setName] = useState("Shree Code Mantra");
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCreateWorkspace = async () => {
    setCreating(true);
    setError(null);
    try {
      await createWorkspace(name);
      await refresh();
    } catch (err) {
      setError(extractErrorMessage(err, "Could not create workspace."));
    } finally {
      setCreating(false);
    }
  };

  if (workspaces.length === 0) {
    return (
      <div className="mx-auto max-w-md pt-8">
        <Card className="p-8">
          <div className="mx-auto mb-5 flex h-12 w-12 items-center justify-center rounded-full bg-brand-50 text-brand-600">
            <LayoutDashboard className="h-6 w-6" />
          </div>
          <h2 className="text-center text-lg font-semibold text-slate-900">
            Create your first workspace
          </h2>
          <p className="mt-2 text-center text-sm text-slate-500">
            A workspace holds one brand, its connected social accounts, campaigns, and analytics.
          </p>

          <div className="mt-6">
            <Label>Workspace name</Label>
            <Input value={name} onChange={(e) => setName(e.target.value)} />
            <HelperText>You can create more workspaces later.</HelperText>
          </div>

          {error && (
            <div className="mt-3 flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2.5 text-sm text-red-700">
              <AlertCircle className="mt-0.5 h-4 w-4 flex-none" />
              {error}
            </div>
          )}

          <Button onClick={handleCreateWorkspace} loading={creating} className="mt-5 w-full">
            {creating ? "Creating..." : "Create workspace"}
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">
          {currentWorkspace?.name ?? "Dashboard"}
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Analytics populate once campaigns are generated, approved, and published (Phase 2–5).
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 xl:grid-cols-4">
        {STAT_CARDS.map((card) => (
          <Card key={card.label} className="p-4 transition-shadow hover:shadow-card-hover">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium uppercase tracking-wide text-slate-400">
                {card.label}
              </span>
              <card.icon className="h-4 w-4 text-slate-300" />
            </div>
            <div className="mt-2.5 text-2xl font-bold text-slate-900">—</div>
          </Card>
        ))}
      </div>

      <EmptyState
        icon={<BarChart3 className="h-6 w-6" />}
        title="No analytics yet"
        description="Charts for reach over time, engagement by platform, and top posts ship with the Analytics module in Phase 5 — once you're generating and publishing content."
      />
    </div>
  );
}
