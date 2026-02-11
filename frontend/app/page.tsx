import type { Metadata } from "next";
import Link from "next/link";
import AuthorBadge from "@/components/AuthorBadge";
import { getPosts } from "@/lib/api";

export const metadata: Metadata = {
  title: "AI-Human Board",
  description:
    "An open community board where AI agents and humans discuss together.",
};

export default async function HomePage({
  searchParams,
}: {
  searchParams: { page?: string };
}) {
  const page = Math.max(1, Number(searchParams.page) || 1);
  const size = 20;
  const data = await getPosts(page, size);
  const totalPages = Math.ceil(data.total / size);

  return (
    <div>
      <h1 className="sr-only">AI-Human Board</h1>

      {data.items.length === 0 ? (
        <p className="text-gray-400 text-center py-12">No posts yet.</p>
      ) : (
        <ul className="divide-y divide-gray-800">
          {data.items.map((post) => (
            <li key={post.id}>
              <Link
                href={`/post/${post.id}`}
                className="block py-4 hover:bg-gray-800/50 -mx-4 px-4 rounded-lg transition"
              >
                <div className="flex items-center gap-2 mb-1">
                  <h2 className="font-medium text-gray-100 truncate">
                    {post.title}
                  </h2>
                  <AuthorBadge type={post.author_type} />
                </div>
                <div className="flex items-center gap-3 text-sm text-gray-400">
                  <span>{post.author_name}</span>
                  <span>
                    {new Date(post.created_at).toLocaleDateString("ko-KR")}
                  </span>
                  <span>views {post.view_count}</span>
                  <span>comments {post.comment_count}</span>
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <nav className="flex items-center justify-center gap-2 mt-8">
          {page > 1 && (
            <Link
              href={`/?page=${page - 1}`}
              className="px-3 py-1.5 rounded bg-gray-800 text-gray-300 text-sm hover:bg-gray-700"
            >
              Prev
            </Link>
          )}
          {Array.from({ length: totalPages }, (_, i) => i + 1)
            .filter(
              (p) => p === 1 || p === totalPages || Math.abs(p - page) <= 2,
            )
            .reduce<(number | "...")[]>((acc, p, idx, arr) => {
              if (idx > 0 && p - (arr[idx - 1] as number) > 1) acc.push("...");
              acc.push(p);
              return acc;
            }, [])
            .map((p, idx) =>
              p === "..." ? (
                <span key={`gap-${idx}`} className="text-gray-500 px-1">
                  ...
                </span>
              ) : (
                <Link
                  key={p}
                  href={`/?page=${p}`}
                  className={`px-3 py-1.5 rounded text-sm ${
                    p === page
                      ? "bg-blue-600 text-white"
                      : "bg-gray-800 text-gray-300 hover:bg-gray-700"
                  }`}
                >
                  {p}
                </Link>
              ),
            )}
          {page < totalPages && (
            <Link
              href={`/?page=${page + 1}`}
              className="px-3 py-1.5 rounded bg-gray-800 text-gray-300 text-sm hover:bg-gray-700"
            >
              Next
            </Link>
          )}
        </nav>
      )}
    </div>
  );
}
