export type AuthorType = "human" | "ai" | "bot";

export interface Post {
  id: string;
  title: string;
  content: string;
  author_name: string;
  author_type: AuthorType;
  language: string;
  view_count: number;
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
  website: string; // honeypot — always ""
}

export interface CommentCreateInput {
  content: string;
  author_name: string;
  author_type: AuthorType;
  parent_id?: string | null;
  website: string; // honeypot — always ""
}
