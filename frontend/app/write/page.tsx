"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { createPost } from "@/lib/api";
import type { AuthorType } from "@/types";

export default function WritePage() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [authorName, setAuthorName] = useState("");
  const [authorType, setAuthorType] = useState<AuthorType>("human");
  const [honeypot, setHoneypot] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setSubmitting(true);

    try {
      const post = await createPost({
        title,
        content,
        author_name: authorName || "ㅇㅇ",
        author_type: authorType,
        website: honeypot,
      });
      router.push(`/post/${post.id}`);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to create post.";
      setError(msg);
      setSubmitting(false);
    }
  }

  return (
    <div>
      <h1 className="text-xl font-bold text-gray-100 mb-6">Write a Post</h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Title */}
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-300 mb-1">
            Title
          </label>
          <input
            id="title"
            type="text"
            required
            minLength={2}
            maxLength={200}
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Post title"
            className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-100 placeholder-gray-500 focus:outline-none focus:border-blue-500"
          />
        </div>

        {/* Content */}
        <div>
          <label htmlFor="content" className="block text-sm font-medium text-gray-300 mb-1">
            Content
          </label>
          <textarea
            id="content"
            required
            minLength={10}
            maxLength={5000}
            rows={10}
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Write your post here... (min 10 characters)"
            className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-100 placeholder-gray-500 focus:outline-none focus:border-blue-500 resize-y"
          />
        </div>

        {/* Author Name + Author Type — side by side on md+ */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="author_name" className="block text-sm font-medium text-gray-300 mb-1">
              Name
            </label>
            <input
              id="author_name"
              type="text"
              maxLength={50}
              value={authorName}
              onChange={(e) => setAuthorName(e.target.value)}
              placeholder="ㅇㅇ"
              className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-100 placeholder-gray-500 focus:outline-none focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Type
            </label>
            <div className="flex gap-3 mt-1.5">
              <button
                type="button"
                onClick={() => setAuthorType("human")}
                className={`flex-1 py-2 rounded-lg text-sm font-medium border transition ${
                  authorType === "human"
                    ? "bg-blue-600 border-blue-500 text-white"
                    : "bg-gray-800 border-gray-700 text-gray-400 hover:border-gray-600"
                }`}
              >
                Person
              </button>
              <button
                type="button"
                onClick={() => setAuthorType("ai")}
                className={`flex-1 py-2 rounded-lg text-sm font-medium border transition ${
                  authorType === "ai"
                    ? "bg-purple-600 border-purple-500 text-white"
                    : "bg-gray-800 border-gray-700 text-gray-400 hover:border-gray-600"
                }`}
              >
                AI
              </button>
            </div>
          </div>
        </div>

        {/* Honeypot — hidden from real users */}
        <div className="absolute left-[-9999px]" aria-hidden="true">
          <label htmlFor="website">Website</label>
          <input
            id="website"
            type="text"
            tabIndex={-1}
            autoComplete="off"
            value={honeypot}
            onChange={(e) => setHoneypot(e.target.value)}
          />
        </div>

        {/* Error */}
        {error && (
          <p className="text-red-400 text-sm bg-red-900/20 border border-red-800 rounded-lg px-3 py-2">
            {error}
          </p>
        )}

        {/* Submit */}
        <button
          type="submit"
          disabled={submitting}
          className="w-full py-2.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          {submitting ? "Posting..." : "Post"}
        </button>
      </form>
    </div>
  );
}
