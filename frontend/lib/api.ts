import type {
  Comment,
  CommentCreateInput,
  PaginatedPosts,
  Post,
  PostCreateInput,
} from "@/types";

/** SSR: 직접 백엔드 호출, CSR: Next.js rewrites 경유 (상대경로) */
const API_BASE =
  typeof window === "undefined"
    ? (process.env.API_URL ?? "http://backend:8000")
    : "";

async function fetcher<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`${res.status}: ${body}`);
  }
  return res.json();
}

// ── Posts ──

export function getPosts(page = 1, size = 20) {
  return fetcher<PaginatedPosts>(
    `/api/posts?page=${page}&size=${size}`,
    { next: { revalidate: 30 } },
  );
}

export function getPost(id: string) {
  return fetcher<Post>(`/api/posts/${id}`, { cache: "no-store" });
}

export function searchPosts(q: string, page = 1, size = 20) {
  return fetcher<PaginatedPosts>(
    `/api/posts/search?q=${encodeURIComponent(q)}&page=${page}&size=${size}`,
  );
}

export function createPost(data: PostCreateInput) {
  return fetcher<Post>("/api/posts", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

// ── Comments ──

export function getComments(postId: string) {
  return fetcher<Comment[]>(`/api/posts/${postId}/comments`, {
    cache: "no-store",
  });
}

export function createComment(postId: string, data: CommentCreateInput) {
  return fetcher<Comment>(`/api/posts/${postId}/comments`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}
