import React from "react";

type Tone = "brand" | "slate" | "green" | "amber" | "red";

const TONE_CLASSES: Record<Tone, string> = {
  brand: "bg-brand-50 text-brand-700 ring-1 ring-inset ring-brand-200",
  slate: "bg-slate-100 text-slate-600 ring-1 ring-inset ring-slate-200",
  green: "bg-emerald-50 text-emerald-700 ring-1 ring-inset ring-emerald-200",
  amber: "bg-amber-50 text-amber-700 ring-1 ring-inset ring-amber-200",
  red: "bg-red-50 text-red-700 ring-1 ring-inset ring-red-200",
};

export function Badge({
  tone = "slate",
  children,
  className = "",
}: {
  tone?: Tone;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <span
      className={[
        "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium",
        TONE_CLASSES[tone],
        className,
      ].join(" ")}
    >
      {children}
    </span>
  );
}
