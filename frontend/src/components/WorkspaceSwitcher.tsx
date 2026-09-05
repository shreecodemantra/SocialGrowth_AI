import { Check, ChevronsUpDown, Plus } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";

import { useClickOutside } from "../hooks/useClickOutside";
import { useWorkspace } from "../hooks/useWorkspace";

function initialsFor(name: string): string {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0]?.toUpperCase())
    .join("");
}

export function WorkspaceSwitcher() {
  const { workspaces, currentWorkspace, setCurrentWorkspace } = useWorkspace();
  const [open, setOpen] = useState(false);
  const ref = useClickOutside<HTMLDivElement>(() => setOpen(false), open);

  if (!currentWorkspace) {
    return (
      <Link
        to="/dashboard"
        className="flex items-center gap-2 rounded-lg border border-dashed border-slate-300 px-3 py-2 text-sm text-slate-500 hover:border-brand-400 hover:text-brand-600"
      >
        <Plus className="h-4 w-4" />
        Create workspace
      </Link>
    );
  }

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center gap-2.5 rounded-lg border border-slate-200 bg-white px-2.5 py-2 text-left shadow-xs transition-colors hover:bg-slate-50"
      >
        <span className="flex h-8 w-8 flex-none items-center justify-center rounded-lg bg-gradient-to-br from-brand-500 to-brand-700 text-xs font-bold text-white">
          {initialsFor(currentWorkspace.name)}
        </span>
        <span className="min-w-0 flex-1">
          <span className="block truncate text-sm font-semibold text-slate-800">
            {currentWorkspace.name}
          </span>
          <span className="block text-xs text-slate-400">Workspace</span>
        </span>
        <ChevronsUpDown className="h-4 w-4 flex-none text-slate-400" />
      </button>

      {open && (
        <div className="absolute left-0 right-0 z-20 mt-1.5 animate-slide-up rounded-lg border border-slate-200 bg-white p-1 shadow-popover">
          {workspaces.map((ws) => (
            <button
              key={ws.id}
              onClick={() => {
                setCurrentWorkspace(ws);
                setOpen(false);
              }}
              className="flex w-full items-center gap-2.5 rounded-md px-2.5 py-2 text-left text-sm hover:bg-slate-50"
            >
              <span className="flex h-6 w-6 flex-none items-center justify-center rounded-md bg-brand-50 text-[10px] font-bold text-brand-700">
                {initialsFor(ws.name)}
              </span>
              <span className="min-w-0 flex-1 truncate text-slate-700">{ws.name}</span>
              {ws.id === currentWorkspace.id && <Check className="h-4 w-4 flex-none text-brand-600" />}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
