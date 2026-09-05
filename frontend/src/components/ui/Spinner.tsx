import { Loader2 } from "lucide-react";

export function Spinner({ className = "h-5 w-5" }: { className?: string }) {
  return <Loader2 className={["animate-spin text-brand-600", className].join(" ")} />;
}

export function FullPageSpinner({ label = "Loading..." }: { label?: string }) {
  return (
    <div className="flex h-screen w-full flex-col items-center justify-center gap-3 bg-slate-50">
      <Spinner className="h-7 w-7" />
      <p className="text-sm text-slate-400">{label}</p>
    </div>
  );
}
