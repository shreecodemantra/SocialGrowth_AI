import { ChevronsUpDown, LogOut } from "lucide-react";
import { useState } from "react";

import { useClickOutside } from "../hooks/useClickOutside";
import { useAuth } from "../hooks/useAuth";

function initialsFor(label: string): string {
  const trimmed = label.trim();
  const parts = trimmed.split(/\s+/);
  if (parts.length > 1) return (parts[0][0] + parts[1][0]).toUpperCase();
  return trimmed.slice(0, 2).toUpperCase();
}

export function UserMenu() {
  const { user, logout } = useAuth();
  const [open, setOpen] = useState(false);
  const ref = useClickOutside<HTMLDivElement>(() => setOpen(false), open);

  if (!user) return null;
  const label = user.full_name || user.email;

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center gap-2.5 rounded-lg px-2 py-2 text-left transition-colors hover:bg-slate-100"
      >
        <span className="flex h-8 w-8 flex-none items-center justify-center rounded-full bg-slate-200 text-xs font-bold text-slate-600">
          {initialsFor(label)}
        </span>
        <span className="min-w-0 flex-1">
          <span className="block truncate text-sm font-medium text-slate-700">{label}</span>
          <span className="block truncate text-xs text-slate-400">{user.email}</span>
        </span>
        <ChevronsUpDown className="h-4 w-4 flex-none text-slate-400" />
      </button>

      {open && (
        <div className="absolute bottom-full left-0 right-0 z-20 mb-1.5 animate-slide-up rounded-lg border border-slate-200 bg-white p-1 shadow-popover">
          <button
            onClick={logout}
            className="flex w-full items-center gap-2.5 rounded-md px-2.5 py-2 text-left text-sm font-medium text-red-600 hover:bg-red-50"
          >
            <LogOut className="h-4 w-4" />
            Sign out
          </button>
        </div>
      )}
    </div>
  );
}
