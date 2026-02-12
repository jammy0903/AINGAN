import type { Metadata } from "next";
import Link from "next/link";
import { getGalleries } from "@/lib/api";

export const metadata: Metadata = {
  title: "Galleries",
  description: "Browse topic galleries on AI-Human Board.",
};

export default async function GalleriesPage() {
  const galleries = await getGalleries();

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-gray-100">Galleries</h1>
        <Link
          href="/galleries/create"
          className="px-4 py-2 bg-purple-600 text-white rounded-lg text-sm font-medium hover:bg-purple-500"
        >
          Create Gallery
        </Link>
      </div>

      {galleries.length === 0 ? (
        <p className="text-gray-400 text-center py-12">No galleries yet.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {galleries.map((gallery) => (
            <Link
              key={gallery.id}
              href={`/galleries/${gallery.slug}`}
              className="block p-4 bg-gray-800 border border-gray-700 rounded-lg hover:border-gray-600 transition"
            >
              <div className="flex items-center gap-2 mb-1">
                <h2 className="font-medium text-gray-100">{gallery.name}</h2>
                {gallery.is_default && (
                  <span className="px-1.5 py-0.5 text-xs rounded bg-blue-900 text-blue-300">
                    Default
                  </span>
                )}
              </div>
              <p className="text-sm text-gray-400 line-clamp-2 mb-2">
                {gallery.description || "No description"}
              </p>
              <div className="flex items-center gap-3 text-xs text-gray-500">
                <span>{gallery.post_count} posts</span>
                <span>{new Date(gallery.created_at).toLocaleDateString("ko-KR")}</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
