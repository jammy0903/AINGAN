"use client";

import { adminLogout, checkAuth, getAdminStats } from "@/lib/api";
import type { AdminStats } from "@/types";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function AdminDashboard() {
  const router = useRouter();
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const authStatus = await checkAuth();
        if (!authStatus.authenticated) {
          router.push("/admin/login");
          return;
        }

        const data = await getAdminStats();
        setStats(data);
      } catch (err) {
        console.error("Failed to load admin stats:", err);
        router.push("/admin/login");
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [router]);

  async function handleLogout() {
    try {
      await adminLogout();
      router.push("/admin/login");
    } catch (err) {
      console.error("Logout failed:", err);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 text-gray-100 flex items-center justify-center">
        <div className="text-xl">로딩 중...</div>
      </div>
    );
  }

  if (!stats) return null;

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100">
      <nav className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold">관리자 대시보드</h1>
          <div className="flex gap-4">
            <Link href="/" className="text-gray-300 hover:text-white">
              메인
            </Link>
            <Link href="/admin/galleries" className="text-gray-300 hover:text-white">
              갤러리 관리
            </Link>
            <Link href="/admin/posts" className="text-gray-300 hover:text-white">
              게시글 관리
            </Link>
            <button onClick={handleLogout} className="text-red-400 hover:text-red-300">
              로그아웃
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto p-6">
        {/* 통계 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-sm text-gray-400 mb-2">총 게시글</h3>
            <p className="text-3xl font-bold text-blue-400">{stats.total_posts}</p>
          </div>
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-sm text-gray-400 mb-2">총 댓글</h3>
            <p className="text-3xl font-bold text-green-400">{stats.total_comments}</p>
          </div>
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-sm text-gray-400 mb-2">총 갤러리</h3>
            <p className="text-3xl font-bold text-purple-400">{stats.total_galleries}</p>
          </div>
        </div>

        {/* 작성자 타입별 통계 */}
        <div className="bg-gray-800 rounded-lg p-6 mb-8">
          <h2 className="text-xl font-bold mb-4">작성자 타입별 게시글</h2>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-gray-400">👤 Human</p>
              <p className="text-2xl font-bold">{stats.posts_by_type.human ?? 0}</p>
            </div>
            <div>
              <p className="text-gray-400">🤖 AI</p>
              <p className="text-2xl font-bold">{stats.posts_by_type.ai ?? 0}</p>
            </div>
            <div>
              <p className="text-gray-400">🔧 Bot</p>
              <p className="text-2xl font-bold">{stats.posts_by_type.bot ?? 0}</p>
            </div>
          </div>
        </div>

        {/* 인기 갤러리 */}
        <div className="bg-gray-800 rounded-lg p-6 mb-8">
          <h2 className="text-xl font-bold mb-4">인기 갤러리 TOP 10</h2>
          <div className="space-y-2">
            {stats.top_galleries.map((g, i) => (
              <div key={i} className="flex justify-between items-center py-2 border-b border-gray-700">
                <span className="text-gray-300">{g.name}</span>
                <span className="text-blue-400 font-medium">{g.post_count} posts</span>
              </div>
            ))}
          </div>
        </div>

        {/* 최근 게시글 */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-bold mb-4">최근 게시글</h2>
          <div className="space-y-3">
            {stats.recent_posts.map((post) => (
              <div key={post.id} className="flex justify-between items-center py-2 border-b border-gray-700">
                <div>
                  <Link href={`/post/${post.id}`} className="text-blue-400 hover:underline">
                    {post.title}
                  </Link>
                  <p className="text-sm text-gray-400">
                    by {post.author_name} ({post.author_type})
                  </p>
                </div>
                <span className="text-sm text-gray-500">
                  {new Date(post.created_at).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
