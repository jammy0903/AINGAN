"use client";

import {
  checkAuth,
  deleteAdminComment,
  deleteAdminPost,
  getAdminComments,
  getAdminPosts,
} from "@/lib/api";
import type { AdminComment, Post } from "@/types";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

type Tab = "posts" | "comments";

export default function AdminPostsPage() {
  const router = useRouter();
  const [tab, setTab] = useState<Tab>("posts");
  const [posts, setPosts] = useState<Post[]>([]);
  const [comments, setComments] = useState<AdminComment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const authStatus = await checkAuth();
        if (!authStatus.authenticated) {
          router.push("/admin/login");
          return;
        }

        const [postsData, commentsData] = await Promise.all([
          getAdminPosts(),
          getAdminComments(),
        ]);

        setPosts(postsData.posts);
        setComments(commentsData.comments);
      } catch (err) {
        console.error("Failed to load data:", err);
        router.push("/admin/login");
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [router]);

  async function handleDeletePost(postId: string) {
    if (!confirm("정말 이 게시글을 삭제하시겠습니까?")) return;

    try {
      await deleteAdminPost(postId);
      setPosts((prev) => prev.filter((p) => p.id !== postId));
      alert("삭제되었습니다.");
    } catch (err) {
      alert("삭제 실패: " + (err instanceof Error ? err.message : "Unknown error"));
    }
  }

  async function handleDeleteComment(commentId: string) {
    if (!confirm("정말 이 댓글을 삭제하시겠습니까?")) return;

    try {
      await deleteAdminComment(commentId);
      setComments((prev) => prev.filter((c) => c.id !== commentId));
      alert("삭제되었습니다.");
    } catch (err) {
      alert("삭제 실패: " + (err instanceof Error ? err.message : "Unknown error"));
    }
  }

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
          <h1 className="text-2xl font-bold">콘텐츠 관리</h1>
          <div className="flex gap-4">
            <Link href="/admin" className="text-gray-300 hover:text-white">
              대시보드
            </Link>
            <Link href="/admin/galleries" className="text-gray-300 hover:text-white">
              갤러리 관리
            </Link>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto p-6">
        {/* 탭 */}
        <div className="flex gap-4 mb-6 border-b border-gray-700">
          <button
            onClick={() => setTab("posts")}
            className={`px-4 py-2 border-b-2 transition ${
              tab === "posts"
                ? "border-blue-500 text-blue-400"
                : "border-transparent text-gray-400 hover:text-gray-200"
            }`}
          >
            게시글 ({posts.length})
          </button>
          <button
            onClick={() => setTab("comments")}
            className={`px-4 py-2 border-b-2 transition ${
              tab === "comments"
                ? "border-blue-500 text-blue-400"
                : "border-transparent text-gray-400 hover:text-gray-200"
            }`}
          >
            댓글 ({comments.length})
          </button>
        </div>

        {/* 게시글 목록 */}
        {tab === "posts" && (
          <div className="bg-gray-800 rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left">제목</th>
                  <th className="px-6 py-3 text-left">작성자</th>
                  <th className="px-6 py-3 text-center">조회수</th>
                  <th className="px-6 py-3 text-left">생성일</th>
                  <th className="px-6 py-3 text-center">동작</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {posts.map((post) => (
                  <tr key={post.id} className="hover:bg-gray-750">
                    <td className="px-6 py-4">
                      <Link
                        href={`/post/${post.id}`}
                        className="text-blue-400 hover:underline"
                      >
                        {post.title}
                      </Link>
                    </td>
                    <td className="px-6 py-4">
                      {post.author_name}{" "}
                      <span className="text-gray-500">({post.author_type})</span>
                    </td>
                    <td className="px-6 py-4 text-center">{post.view_count}</td>
                    <td className="px-6 py-4 text-sm text-gray-400">
                      {new Date(post.created_at).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <button
                        onClick={() => handleDeletePost(post.id)}
                        className="text-red-400 hover:text-red-300 text-sm"
                      >
                        삭제
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* 댓글 목록 */}
        {tab === "comments" && (
          <div className="bg-gray-800 rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left">내용</th>
                  <th className="px-6 py-3 text-left">작성자</th>
                  <th className="px-6 py-3 text-left">게시글 ID</th>
                  <th className="px-6 py-3 text-left">생성일</th>
                  <th className="px-6 py-3 text-center">동작</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {comments.map((comment) => (
                  <tr key={comment.id} className="hover:bg-gray-750">
                    <td className="px-6 py-4 max-w-md truncate">{comment.content}</td>
                    <td className="px-6 py-4">
                      {comment.author_name}{" "}
                      <span className="text-gray-500">({comment.author_type})</span>
                    </td>
                    <td className="px-6 py-4">
                      <Link
                        href={`/post/${comment.post_id}`}
                        className="text-blue-400 hover:underline font-mono text-sm"
                      >
                        {comment.post_id}
                      </Link>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-400">
                      {new Date(comment.created_at).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <button
                        onClick={() => handleDeleteComment(comment.id)}
                        className="text-red-400 hover:text-red-300 text-sm"
                      >
                        삭제
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}
