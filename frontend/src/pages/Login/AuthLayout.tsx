import { BarChart3, CalendarClock, Sparkles } from "lucide-react";
import React from "react";

const FEATURES = [
  { icon: Sparkles, text: "AI-generated, platform-specific content in seconds" },
  { icon: CalendarClock, text: "Approve once, publish everywhere on schedule" },
  { icon: BarChart3, text: "Real analytics — what's working, and what to post next" },
];

export function AuthLayout({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen bg-slate-50">
      <div className="relative hidden w-[44%] flex-col justify-between overflow-hidden bg-gradient-to-br from-brand-700 via-brand-800 to-slate-950 p-12 text-white lg:flex">
        <div
          className="pointer-events-none absolute inset-0 opacity-[0.07]"
          style={{
            backgroundImage:
              "radial-gradient(circle at 1px 1px, white 1px, transparent 0)",
            backgroundSize: "28px 28px",
          }}
        />

        <div className="relative flex items-center gap-2.5">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-white/15 text-base font-bold backdrop-blur">
            S
          </span>
          <span className="text-lg font-bold">SocialGrowth AI</span>
        </div>

        <div className="relative">
          <h2 className="text-3xl font-bold leading-tight">
            The AI social media manager for teams that ship.
          </h2>
          <p className="mt-3 max-w-sm text-sm text-brand-100">
            Research, write, design, schedule, and analyze every post — across
            Instagram, LinkedIn, Facebook, and YouTube — from one workspace.
          </p>

          <ul className="mt-8 space-y-4">
            {FEATURES.map(({ icon: Icon, text }) => (
              <li key={text} className="flex items-start gap-3 text-sm text-brand-50">
                <span className="mt-0.5 flex h-6 w-6 flex-none items-center justify-center rounded-md bg-white/10">
                  <Icon className="h-3.5 w-3.5" />
                </span>
                {text}
              </li>
            ))}
          </ul>
        </div>

        <p className="relative text-xs text-brand-200">
          Built for Shree Code Mantra &amp; growing brands like it.
        </p>
      </div>

      <div className="flex flex-1 flex-col items-center justify-center px-6 py-12 sm:px-10">
        <div className="w-full max-w-sm">
          <div className="mb-8 flex items-center gap-2.5 lg:hidden">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-brand-500 to-brand-700 text-sm font-bold text-white">
              S
            </span>
            <span className="text-base font-bold text-slate-900">SocialGrowth AI</span>
          </div>

          <h1 className="text-xl font-bold text-slate-900">{title}</h1>
          <p className="mt-1 text-sm text-slate-500">{subtitle}</p>

          <div className="mt-7">{children}</div>
        </div>
      </div>
    </div>
  );
}
