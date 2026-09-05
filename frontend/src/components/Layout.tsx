import {
  BarChart3,
  Calendar,
  FileText,
  LayoutDashboard,
  Lightbulb,
  type LucideIcon,
  Megaphone,
  Menu,
  Palette,
  Settings as SettingsIcon,
  Share2,
  Sparkles,
  TrendingUp,
  Users,
} from "lucide-react";
import { useEffect, useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";

import { UserMenu } from "./UserMenu";
import { WorkspaceSwitcher } from "./WorkspaceSwitcher";

interface NavItem {
  to: string;
  label: string;
  icon: LucideIcon;
}

interface NavGroup {
  label: string;
  items: NavItem[];
}

const NAV_GROUPS: NavGroup[] = [
  { label: "Overview", items: [{ to: "/dashboard", label: "Dashboard", icon: LayoutDashboard }] },
  {
    label: "Create",
    items: [
      { to: "/campaigns", label: "Campaigns", icon: Megaphone },
      { to: "/content-generator", label: "Content Generator", icon: Sparkles },
      { to: "/calendar", label: "Calendar", icon: Calendar },
    ],
  },
  {
    label: "Manage",
    items: [
      { to: "/posts", label: "Posts", icon: FileText },
      { to: "/social-accounts", label: "Social Accounts", icon: Share2 },
    ],
  },
  {
    label: "Measure",
    items: [
      { to: "/analytics", label: "Analytics", icon: BarChart3 },
      { to: "/insights", label: "AI Insights", icon: Lightbulb },
      { to: "/recommendations", label: "Recommendations", icon: TrendingUp },
    ],
  },
  {
    label: "Workspace",
    items: [
      { to: "/brand-settings", label: "Brand Settings", icon: Palette },
      { to: "/team", label: "Team", icon: Users },
      { to: "/settings", label: "Settings", icon: SettingsIcon },
    ],
  },
];

const ALL_ITEMS = NAV_GROUPS.flatMap((g) => g.items);

function navLinkClass({ isActive }: { isActive: boolean }) {
  return [
    "group flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm font-medium transition-colors",
    isActive
      ? "bg-brand-50 text-brand-700"
      : "text-slate-600 hover:bg-slate-100 hover:text-slate-900",
  ].join(" ");
}

function SidebarContent() {
  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center gap-2.5 px-4 py-5">
        <span className="flex h-8 w-8 flex-none items-center justify-center rounded-lg bg-gradient-to-br from-brand-500 to-brand-700 text-sm font-bold text-white shadow-xs">
          S
        </span>
        <div className="min-w-0">
          <div className="truncate text-sm font-bold text-slate-900">SocialGrowth AI</div>
          <div className="truncate text-[11px] text-slate-400">Social Automation Platform</div>
        </div>
      </div>

      <div className="px-3 pb-3">
        <WorkspaceSwitcher />
      </div>

      <nav className="flex-1 space-y-5 overflow-y-auto px-3 pb-4">
        {NAV_GROUPS.map((group) => (
          <div key={group.label}>
            <div className="px-2.5 pb-1.5 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              {group.label}
            </div>
            <div className="space-y-0.5">
              {group.items.map((item) => (
                <NavLink key={item.to} to={item.to} className={navLinkClass}>
                  <item.icon className="h-[18px] w-[18px] flex-none" strokeWidth={2} />
                  <span className="truncate">{item.label}</span>
                </NavLink>
              ))}
            </div>
          </div>
        ))}
      </nav>

      <div className="border-t border-slate-200 p-2">
        <UserMenu />
      </div>
    </div>
  );
}

export function Layout() {
  const location = useLocation();
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  useEffect(() => {
    setMobileNavOpen(false);
  }, [location.pathname]);

  const pageTitle = ALL_ITEMS.find((item) => location.pathname.startsWith(item.to))?.label ?? "";

  return (
    <div className="flex h-screen bg-slate-50">
      {/* Desktop sidebar */}
      <aside className="hidden w-72 flex-none border-r border-slate-200 bg-white lg:block">
        <SidebarContent />
      </aside>

      {/* Mobile sidebar (slide-over) */}
      {mobileNavOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div
            className="absolute inset-0 animate-fade-in bg-slate-900/50"
            onClick={() => setMobileNavOpen(false)}
          />
          <aside className="absolute inset-y-0 left-0 w-72 animate-slide-in-left bg-white shadow-popover">
            <SidebarContent />
          </aside>
        </div>
      )}

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-14 flex-none items-center gap-3 border-b border-slate-200 bg-white px-4 lg:px-8">
          <button
            type="button"
            onClick={() => setMobileNavOpen(true)}
            className="-ml-1 rounded-lg p-1.5 text-slate-500 hover:bg-slate-100 lg:hidden"
            aria-label="Open navigation"
          >
            <Menu className="h-5 w-5" />
          </button>
          <h1 className="truncate text-sm font-semibold text-slate-800">{pageTitle}</h1>
        </header>

        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
          <div className="mx-auto max-w-7xl">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}

