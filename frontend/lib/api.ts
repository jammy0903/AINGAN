import type {
  AdminComment,
  AdminStats,
  Comment,
  CommentCreateInput,
  Gallery,
  GalleryCreateInput,
  GalleryListItem,
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

// ── Galleries ──

export function getGalleries() {
  return fetcher<GalleryListItem[]>("/api/galleries", {
    next: { revalidate: 30 },
  });
}

export function getGallery(slug: string) {
  return fetcher<Gallery>(`/api/galleries/${slug}`, { cache: "no-store" });
}

export function getGalleryPosts(slug: string, page = 1, size = 20) {
  return fetcher<PaginatedPosts>(
    `/api/galleries/${slug}/posts?page=${page}&size=${size}`,
    { next: { revalidate: 30 } },
  );
}

export function createGallery(data: GalleryCreateInput) {
  return fetcher<Gallery>("/api/galleries", {
    method: "POST",
    body: JSON.stringify(data),
  });
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

// ── Admin Auth ──

export async function adminLogin(password: string) {
  const res = await fetch(`${API_BASE}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ password }),
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`${res.status}: ${body}`);
  }
  return res.json();
}

export async function adminLogout() {
  const res = await fetch(`${API_BASE}/api/auth/logout`, {
    method: "POST",
    credentials: "include",
  });
  if (!res.ok) throw new Error(`Logout failed: ${res.status}`);
  return res.json();
}

export async function checkAuth() {
  const res = await fetch(`${API_BASE}/api/auth/check`, {
    credentials: "include",
  });
  if (!res.ok) return { authenticated: false };
  return res.json();
}

// ── Admin API ──

export function getAdminStats() {
  return fetcher<AdminStats>("/api/admin/stats", {
    credentials: "include",
    cache: "no-store",
  });
}

export function getAdminGalleries() {
  return fetcher<{ galleries: Gallery[] }>("/api/admin/galleries", {
    credentials: "include",
    cache: "no-store",
  });
}

export function getAdminPosts(page = 1, size = 50) {
  return fetcher<{ posts: Post[]; total: number; page: number; size: number }>(
    `/api/admin/posts?page=${page}&size=${size}`,
    { credentials: "include", cache: "no-store" },
  );
}

export function getAdminComments(page = 1, size = 50) {
  return fetcher<{ comments: AdminComment[]; total: number; page: number; size: number }>(
    `/api/admin/comments?page=${page}&size=${size}`,
    { credentials: "include", cache: "no-store" },
  );
}

export async function deleteAdminPost(postId: string) {
  const res = await fetch(`${API_BASE}/api/admin/posts/${postId}`, {
    method: "DELETE",
    credentials: "include",
  });
  if (!res.ok) throw new Error(`Delete failed: ${res.status}`);
  return res.json();
}

export async function deleteAdminComment(commentId: string) {
  const res = await fetch(`${API_BASE}/api/admin/comments/${commentId}`, {
    method: "DELETE",
    credentials: "include",
  });
  if (!res.ok) throw new Error(`Delete failed: ${res.status}`);
  return res.json();
}
