"use client";

import { checkAuth, getAdminGalleries } from "@/lib/api";
import type { Gallery } from "@/types";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function AdminGalleriesPage() {
  const router = useRouter();
  const [galleries, setGalleries] = useState<Gallery[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const authStatus = await checkAuth();
        if (!authStatus.authenticated) {
          router.push("/admin/login");
          return;
        }

        const data = await getAdminGalleries();
        setGalleries(data.galleries);
      } catch (err) {
        console.error("Failed to load galleries:", err);
        router.push("/admin/login");
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [router]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 text-gray-100 flex items-center justify-center">
        <div className="text-xl">로딩 중...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100">
      <nav className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold">갤러리 관리</h1>
          <div className="flex gap-4">
            <Link href="/admin" className="text-gray-300 hover:text-white">
              대시보드
            </Link>
            <Link href="/admin/posts" className="text-gray-300 hover:text-white">
              게시글 관리
            </Link>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto p-6">
        <div className="mb-6 flex justify-between items-center">
          <h2 className="text-xl font-bold">전체 갤러리 ({galleries.length})</h2>
          <Link
            href="/galleries/create"
            className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded"
          >
            + 새 갤러리 만들기
          </Link>
        </div>

        <div className="bg-gray-800 rounded-lg overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left">Slug</th>
                <th className="px-6 py-3 text-left">이름</th>
                <th className="px-6 py-3 text-left">설명</th>
                <th className="px-6 py-3 text-center">게시글 수</th>
                <th className="px-6 py-3 text-center">기본</th>
                <th className="px-6 py-3 text-left">생성자</th>
                <th className="px-6 py-3 text-left">생성일</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {galleries.map((gallery) => (
                <tr key={gallery.id} className="hover:bg-gray-750">
                  <td className="px-6 py-4">
                    <Link
                      href={`/galleries/${gallery.slug}`}
                      className="text-blue-400 hover:underline font-mono"
                    >
                      {gallery.slug}
                    </Link>
                  </td>
                  <td className="px-6 py-4 font-medium">{gallery.name}</td>
                  <td className="px-6 py-4 text-sm text-gray-400 max-w-xs truncate">
                    {gallery.description}
                  </td>
                  <td className="px-6 py-4 text-center">{gallery.post_count}</td>
                  <td className="px-6 py-4 text-center">
                    {gallery.is_default ? (
                      <span className="bg-green-900/50 text-green-300 px-2 py-1 rounded text-xs">
                        DEFAULT
                      </span>
                    ) : (
                      <span className="text-gray-600">-</span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm">
                    {gallery.creator_name}{" "}
                    <span className="text-gray-500">({gallery.creator_type})</span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-400">
                    {new Date(gallery.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
}
