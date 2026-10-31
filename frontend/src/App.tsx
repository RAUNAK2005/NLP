import { Activity, BarChart3, BookOpen, History, Settings, UploadCloud } from "lucide-react";
import { NavLink, Outlet } from "react-router-dom";

const links = [
  { to: "/", label: "Overview", icon: Activity },
  { to: "/new", label: "New Evaluation", icon: UploadCloud },
  { to: "/history", label: "History", icon: History },
  { to: "/methodology", label: "Methodology", icon: BookOpen },
  { to: "/settings", label: "Settings", icon: Settings },
];

export default function App() {
  return (
    <div className="min-h-screen bg-[#f6f7fb]">
      <header className="sticky top-0 z-20 border-b border-line bg-white/95 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
          <NavLink to="/" className="flex items-center gap-3">
            <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent text-white">
              <BarChart3 size={22} />
            </span>
            <span>
              <span className="block text-sm font-semibold uppercase tracking-wide text-accent">Evaluation</span>
              <span className="block text-lg font-bold text-ink">Synthetic Dataset Quality</span>
            </span>
          </NavLink>
          <nav className="hidden items-center gap-1 md:flex">
            {links.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition ${
                    isActive ? "bg-[#e9f5f3] text-accent" : "text-muted hover:bg-white hover:text-ink"
                  }`
                }
              >
                <Icon size={16} />
                {label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
        <Outlet />
      </main>
    </div>
  );
}

