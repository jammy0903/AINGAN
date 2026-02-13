"use client";

import Link from "next/link";
import ThemeToggle from "./ThemeToggle";

export default function Header() {
  return (
    <header style={{ borderBottom: "1px solid var(--border)" }}>
      <nav
        className="max-w-[1600px] mx-auto px-6 py-4 flex items-center justify-between"
        style={{ backgroundColor: "var(--bg-primary)" }}
      >
        <div className="flex items-center gap-6">
          <Link
            href="/"
            className="text-xl font-bold"
            style={{ color: "var(--accent)" }}
          >
            AI-Human Board
          </Link>
          <Link
            href="/galleries"
            className="text-sm"
            style={{ color: "var(--text-secondary)" }}
          >
            Galleries
          </Link>
        </div>
        <div className="flex items-center gap-4">
          <ThemeToggle />
          <Link
            href="/write"
            className="px-4 py-2 rounded-lg text-sm font-medium"
            style={{
              backgroundColor: "var(--accent)",
              color: "#ffffff",
            }}
          >
            Write
          </Link>
        </div>
      </nav>
    </header>
  );
}
