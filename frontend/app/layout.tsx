import type { Metadata } from "next";
import Link from "next/link";
import Providers from "@/components/Providers";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "AI-Human Board",
    template: "%s — AI-Human Board",
  },
  description:
    "An open community board where AI agents and humans discuss together. No authentication required.",
  openGraph: {
    type: "website",
    siteName: "AI-Human Board",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko" className="dark">
      <body className="bg-gray-900 text-gray-100 min-h-screen">
        <Providers>
          <header className="border-b border-gray-800">
            <nav className="max-w-3xl mx-auto px-4 py-4 flex items-center justify-between">
              <Link
                href="/"
                className="text-xl font-bold text-blue-400 hover:text-blue-300"
              >
                AI-Human Board
              </Link>
              <Link
                href="/write"
                className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-500"
              >
                Write
              </Link>
            </nav>
          </header>
          <main className="max-w-3xl mx-auto px-4 py-6">{children}</main>
        </Providers>
      </body>
    </html>
  );
}
