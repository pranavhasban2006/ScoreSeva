import { useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import {
  LayoutDashboard, ShieldCheck, TrendingUp,
  MessageSquareText, Activity, Menu, X, Zap, PlayCircle, BookOpen, Quote
} from "lucide-react";
import { getDemoGuide } from "../lib/api";

const NAV_ITEMS = [
  { to: "/",           icon: LayoutDashboard,   label: "Score Applicant" },
  { to: "/fraud",      icon: ShieldCheck,       label: "Fraud Check"     },
  { to: "/trajectory", icon: TrendingUp,        label: "Score Roadmap"   },
  { to: "/nlp",        icon: MessageSquareText, label: "NLP Psychometric" },
  { to: "/health",     icon: Activity,          label: "API Health"      },
];

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [demoModalOpen, setDemoModalOpen] = useState(false);
  const [demoData, setDemoData] = useState(null);
  const [loadingDemo, setLoadingDemo] = useState(false);

  const handleOpenDemo = async () => {
    setDemoModalOpen(true);
    if (!demoData) {
      setLoadingDemo(true);
      try {
        const res = await getDemoGuide();
        setDemoData(res.data);
      } catch (err) {
        console.error("Failed to load demo guide", err);
      } finally {
        setLoadingDemo(false);
      }
    }
  };

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden relative">
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

      {/* ── Demo Mode FAB ── */}
      <button 
        onClick={handleOpenDemo}
        className="fixed bottom-6 right-6 bg-brand-dark text-white rounded-full p-4 shadow-xl hover:bg-orange-700 transition-all z-40 flex items-center justify-center group animate-bounce"
        style={{ animationDuration: '3s' }}
      >
        <PlayCircle className="w-6 h-6 group-hover:scale-110 transition-transform" />
        <span className="max-w-0 overflow-hidden group-hover:max-w-xs transition-all duration-300 ease-in-out whitespace-nowrap group-hover:ml-2 font-bold text-sm">
          Launch Demo Guide
        </span>
      </button>

      {/* ── Demo Modal ── */}
      {demoModalOpen && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4 backdrop-blur-sm">
          <div className="bg-white rounded-2xl w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col shadow-2xl animate-in fade-in zoom-in duration-200">
            <div className="px-6 py-4 border-b flex justify-between items-center bg-gray-50">
              <div className="flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-brand-orange" />
                <h2 className="text-xl font-bold text-gray-800">Demo Guide</h2>
              </div>
              <button onClick={() => setDemoModalOpen(false)} className="text-gray-400 hover:text-gray-600 bg-gray-200 hover:bg-gray-300 rounded-full p-1 transition-colors">
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="p-6 overflow-y-auto flex-1">
              {loadingDemo ? (
                <div className="flex justify-center py-12">
                  <div className="w-8 h-8 border-4 border-brand-orange border-t-transparent rounded-full animate-spin"></div>
                </div>
              ) : demoData ? (
                <div className="space-y-8">
                  <div className="bg-brand-orange-bg border border-orange-100 p-4 rounded-xl text-brand-dark flex items-start gap-3">
                    <Quote className="w-6 h-6 flex-shrink-0 mt-1 opacity-50" />
                    <p className="font-semibold text-lg italic">{demoData.story}</p>
                  </div>

                  <div className="space-y-6">
                    <h3 className="font-bold text-gray-800 uppercase text-sm tracking-wider flex items-center gap-2">
                      <span className="w-4 h-px bg-gray-300"></span> 
                      4-Step Presentation Script
                      <span className="flex-1 h-px bg-gray-300"></span>
                    </h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {demoData.demo_steps.map((step, idx) => (
                        <div key={idx} className="border border-gray-200 rounded-xl p-4 hover:border-brand-orange transition-colors bg-white shadow-sm">
                          <div className="flex justify-between items-start mb-2">
                            <span className="bg-gray-800 text-white text-xs font-bold px-2 py-1 rounded">Step {step.step}</span>
                          </div>
                          <h4 className="font-bold text-gray-900 mb-1">{step.title}</h4>
                          <p className="text-xs font-medium text-brand-orange mb-3 pb-2 border-b border-gray-100 font-mono">{step.url}</p>
                          <p className="text-sm text-gray-600 leading-relaxed mb-3">{step.what_to_say}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h3 className="font-bold text-gray-800 uppercase text-sm tracking-wider mb-4 flex items-center gap-2">
                      <span className="w-4 h-px bg-gray-300"></span> 
                      Key Numbers to Memorize
                      <span className="flex-1 h-px bg-gray-300"></span>
                    </h3>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                      {Object.entries(demoData.key_numbers_to_quote).map(([key, val]) => (
                        <div key={key} className="bg-gray-50 rounded-lg p-3 border border-gray-100">
                          <p className="text-[10px] uppercase text-gray-500 font-bold mb-1">{key.replace(/_/g, ' ')}</p>
                          <p className="text-sm font-semibold text-gray-800">{val}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                </div>
              ) : (
                <p className="text-red-500">Failed to load demo guide.</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
