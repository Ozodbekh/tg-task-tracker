import { createContext, useContext, useEffect, useState } from "react";
import type { ReactNode } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";

import { useAuth } from "@/hooks/AuthContext";
import { useTheme } from "@/hooks/useTheme";
import { initials } from "@/lib/format";

const MenuContext = createContext<() => void>(() => {});

const LINKS = [
  { to: "/", label: "Boshqaruv paneli", icon: "◧", end: true },
  { to: "/tasks", label: "Topshiriqlar", icon: "☑", end: false },
  { to: "/employees", label: "Xodimlar", icon: "☺", end: false },
  { to: "/chats", label: "Chat va guruhlar", icon: "✉", end: false },
  { to: "/unresolved", label: "Aniqlanmaganlar", icon: "⚠", end: false },
];

export function Layout() {
  const { session, signOut } = useAuth();
  const { theme, toggle } = useTheme();
  const [menuOpen, setMenuOpen] = useState(false);
  const location = useLocation();

  useEffect(() => setMenuOpen(false), [location.pathname]);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") setMenuOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return (
    <div className="app">
      <div
        className={menuOpen ? "scrim visible" : "scrim"}
        role="presentation"
        onClick={() => setMenuOpen(false)}
      />

      <aside className={menuOpen ? "sidebar open" : "sidebar"}>
        <div className="brand">
          <span className="brand-mark">TT</span>
          <span className="stack">
            <span className="brand-name">Task Tracker</span>
            <span className="brand-sub">Telegram nazorati</span>
          </span>
        </div>

        <nav className="nav">
          {LINKS.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
            >
              <span className="nav-icon">{link.icon}</span>
              {link.label}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <button type="button" className="ghost-button" onClick={toggle}>
            {theme === "dark" ? "☀ Yorug' rejim" : "☾ Tungi rejim"}
          </button>
          <div className="user-card">
            <span className="avatar">{initials(session?.username ?? "?")}</span>
            <span className="stack">
              <span>{session?.username}</span>
              <span className="cell-sub">Boshqaruvchi</span>
            </span>
          </div>
          <button type="button" className="ghost-button" onClick={() => void signOut()}>
            Chiqish
          </button>
        </div>
      </aside>

      <main className="main">
        <MenuContext value={() => setMenuOpen(true)}>
          <Outlet />
        </MenuContext>
      </main>
    </div>
  );
}

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  filters?: ReactNode;
  actions?: ReactNode;
}

export function PageHeader({ title, subtitle, filters, actions }: PageHeaderProps) {
  return (
    <header className="topbar">
      <div className="topbar-row">
        <div className="row" style={{ minWidth: 0 }}>
          <MenuButton />
          <div className="stack">
            <h1 className="page-title">{title}</h1>
            {subtitle && <p className="page-subtitle">{subtitle}</p>}
          </div>
        </div>
        {actions}
      </div>
      {filters && <div className="filters-scroll">{filters}</div>}
    </header>
  );
}

function MenuButton() {
  const openMenu = useContext(MenuContext);
  return (
    <button type="button" className="menu-button" aria-label="Menyuni ochish" onClick={openMenu}>
      ☰
    </button>
  );
}
