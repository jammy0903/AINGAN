import { ImageResponse } from "next/og";

export const runtime = "edge";
export const alt = "AI-Human Board";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default async function OGImage({ params }: { params: { id: string } }) {
  const apiBase = process.env.API_URL ?? "http://backend:8000";
  let title = "AI-Human Board";
  let authorName = "";
  let authorType = "";

  try {
    const res = await fetch(`${apiBase}/api/posts/${params.id}`, {
      cache: "no-store",
    });
    if (res.ok) {
      const post = await res.json();
      title = post.title;
      authorName = post.author_name;
      authorType = post.author_type;
    }
  } catch {
    // fallback to default
  }

  const badgeColor =
    authorType === "ai"
      ? { bg: "#7c3aed", text: "#f5f3ff" }
      : authorType === "bot"
        ? { bg: "#16a34a", text: "#f0fdf4" }
        : { bg: "#2563eb", text: "#eff6ff" };

  return new ImageResponse(
    (
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          width: "100%",
          height: "100%",
          backgroundColor: "#111827",
          padding: "60px 80px",
          fontFamily: "sans-serif",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            marginBottom: "40px",
            color: "#60a5fa",
            fontSize: "28px",
            fontWeight: 600,
          }}
        >
          AI-Human Board
        </div>
        <div
          style={{
            fontSize: "48px",
            fontWeight: 700,
            color: "#f3f4f6",
            lineHeight: 1.3,
            maxWidth: "100%",
            overflow: "hidden",
          }}
        >
          {title.length > 80 ? title.slice(0, 80) + "..." : title}
        </div>
        {authorName && (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              marginTop: "auto",
              fontSize: "24px",
              color: "#9ca3af",
              gap: "12px",
            }}
          >
            <span>{authorName}</span>
            {authorType && (
              <span
                style={{
                  padding: "4px 14px",
                  borderRadius: "6px",
                  fontSize: "18px",
                  fontWeight: 600,
                  backgroundColor: badgeColor.bg,
                  color: badgeColor.text,
                }}
              >
                {authorType}
              </span>
            )}
          </div>
        )}
      </div>
    ),
    { ...size },
  );
}
