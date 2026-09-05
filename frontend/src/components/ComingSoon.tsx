import { Sparkles } from "lucide-react";

import { Badge } from "./ui/Badge";
import { EmptyState } from "./ui/EmptyState";

export function ComingSoon({ title, phase }: { title: string; phase: string }) {
  return (
    <EmptyState
      icon={<Sparkles className="h-6 w-6" />}
      title={title}
      description="This screen isn't built yet — the Phase 1 foundation (auth, workspaces, brand profile) is live now, and this ships in a later phase."
      action={<Badge tone="brand">Ships in {phase}</Badge>}
    />
  );
}
