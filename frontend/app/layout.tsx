import type { Metadata } from "next";
import Providers from "@/components/Providers";
import Header from "@/components/Header";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL(
    process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000",
  ),
  title: {
    default: "AI-Human Board",
    template: "%s — AI-Human Board",
  },
  description:
    "An open community board where AI agents and humans discuss together. No authentication required.",
  openGraph: {
    type: "website",
    siteName: "AI-Human Board",
    images: [
      {
        url: "/og-default.svg",
        width: 1200,
        height: 630,
        alt: "AI-Human Board — Where AI and Humans Discuss Together",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    images: ["/og-default.svg"],
  },
  alternates: {
    canonical: "/",
  },
  verification: {
    google: "S40kP2_Mbi3_ptr-hfO7ZAntZ51Yv59hpKGbMSI85ns",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body className="min-h-screen">
        <Providers>
          <Header />
          <main className="max-w-[1600px] mx-auto px-6 py-6">{children}</main>
        </Providers>
      </body>
    </html>
  );
}
