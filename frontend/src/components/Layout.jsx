import { useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import {
  LayoutDashboard, ShieldCheck, TrendingUp,
  MessageSquareText, Activity, Menu, X, Zap,
} from "lucide-react";

const NAV_ITEMS = [
  { to: "/",           icon: LayoutDashboard,   label: "Score Applicant" },
  { to: "/fraud",      icon: ShieldCheck,       label: "Fraud Check"     },
  { to: "/trajectory", icon: TrendingUp,        label: "Score Roadmap"   },
  { to: "/nlp",        icon: MessageSquareText, label: "NLP Psychometric" },
  { to: "/health",     icon: Activity,          label: "API Health"      },
];

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden">
      {/* ── Mobile overlay ── */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/40 z-20 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* ── Sidebar ── */}
      <aside
        className={`
          fixed lg:static inset-y-0 left-0 z-30
          w-64 bg-white border-r border-gray-100
          flex flex-col transition-transform duration-200
          ${sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}
        `}
      >
        {/* Logo */}
        <div className="flex items-center gap-3 px-6 py-5 border-b border-gray-100">
          <div className="w-9 h-9 rounded-xl bg-brand-orange
                          flex items-center justify-center flex-shrink-0">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <div>
            <p className="font-bold text-gray-900 text-base leading-tight">
              ScoreSeva
            </p>
            <p className="text-xs text-gray-400 leading-tight">
              Alternate Credit AI
            </p>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-xl
                 text-sm font-medium transition-colors duration-150
                 ${isActive
                   ? "bg-brand-orange-bg text-brand-orange"
                   : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                 }`
              }
            >
              <Icon className="w-4 h-4 flex-shrink-0" />
              {label}
            </NavLink>
          ))}
        </nav>

        {/* Footer tag */}
        <div className="px-6 py-4 border-t border-gray-100">
          <p className="text-xs text-gray-400">
            190M credit-invisible Indians
          </p>
          <p className="text-xs font-semibold text-brand-orange mt-0.5">
            ScoreSeva changes that.
          </p>
        </div>
      </aside>

      {/* ── Main area ── */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Topbar */}
        <header className="bg-white border-b border-gray-100
                           px-4 lg:px-6 py-3 flex items-center
                           justify-between flex-shrink-0">
          <button
            className="lg:hidden p-2 rounded-lg hover:bg-gray-100
                       transition-colors"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="w-5 h-5 text-gray-600" />
          </button>

          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-gray-500 hidden sm:block">
              AI-Driven Alternate Credit Scoring
            </span>
            <span className="badge bg-brand-orange-bg text-brand-orange">
              v1.0 · Hackathon Build
            </span>
          </div>

          <div className="w-8 lg:hidden" /> {/* spacer */}
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-4 lg:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
