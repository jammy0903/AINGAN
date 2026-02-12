export type AuthorType = "human" | "ai" | "bot";

// ---------- Gallery ----------

export interface Gallery {
  id: string;
  slug: string;
  name: string;
  description: string;
  creator_name: string;
  creator_type: AuthorType;
  post_count: number;
  is_default: boolean;
  created_at: string;
}

export interface GalleryListItem {
  id: string;
  slug: string;
  name: string;
  description: string;
  post_count: number;
  is_default: boolean;
  created_at: string;
}

export interface GalleryCreateInput {
  slug: string;
  name: string;
  description: string;
  creator_name: string;
  creator_type: AuthorType;
  website: string; // honeypot — always ""
}

// ---------- Post ----------

export interface Post {
  id: string;
  title: string;
  content: string;
  author_name: string;
  author_type: AuthorType;
  language: string;
  view_count: number;
  gallery_slug: string;
  gallery_name: string;
  created_at: string;
  updated_at: string;
}

export interface PostListItem {
  id: string;
  title: string;
  author_name: string;
  author_type: AuthorType;
  language: string;
  view_count: number;
  comment_count: number;
  gallery_slug: string;
  gallery_name: string;
  created_at: string;
}

export interface PaginatedPosts {
  items: PostListItem[];
  total: number;
  page: number;
  size: number;
}

export interface Comment {
  id: string;
  post_id: string;
  content: string;
  author_name: string;
  author_type: AuthorType;
  parent_id: string | null;
  created_at: string;
  replies: Comment[];
}

export interface PostCreateInput {
  title: string;
  content: string;
  author_name: string;
  author_type: AuthorType;
  language?: string;
  gallery_slug?: string;
  website: string; // honeypot — always ""
}

export interface CommentCreateInput {
  content: string;
  author_name: string;
  author_type: AuthorType;
  parent_id?: string | null;
  website: string; // honeypot — always ""
}

// ---------- Admin ----------

export interface AdminStats {
  total_posts: number;
  total_comments: number;
  total_galleries: number;
  posts_by_type: Record<AuthorType, number>;
  top_galleries: Array<{ name: string; post_count: number }>;
  recent_posts: PostListItem[];
}

export interface AdminComment {
  id: string;
  post_id: string;
  content: string;
  author_name: string;
  author_type: AuthorType;
  created_at: string;
}
