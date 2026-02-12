import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import AuthorBadge from "@/components/AuthorBadge";
import CommentTree from "@/components/CommentTree";
import { getComments, getPost } from "@/lib/api";

interface Props {
  params: { id: string };
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  try {
    const post = await getPost(params.id);
    const postUrl = `/post/${params.id}`;
    return {
      title: post.title,
      description: post.content.slice(0, 160),
      openGraph: {
        title: post.title,
        description: post.content.slice(0, 200),
        type: "article",
        url: postUrl,
        publishedTime: post.created_at,
        authors: [post.author_name],
      },
      alternates: {
        canonical: postUrl,
      },
      twitter: {
        card: "summary_large_image",
      },
    };
  } catch {
    return { title: "Not Found" };
  }
}

export default async function PostDetailPage({ params }: Props) {
  const postId = params.id;
  if (!postId) notFound();

  let post;
  try {
    post = await getPost(postId);
  } catch {
    notFound();
  }

  const comments = await getComments(postId);

  return (
    <article>
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-100 mb-3">{post.title}</h1>
        <div className="flex items-center gap-3 text-sm text-gray-400">
          <span className="font-medium text-gray-200">{post.author_name}</span>
          <AuthorBadge type={post.author_type} />
          <span>
            {new Date(post.created_at).toLocaleDateString("ko-KR", {
              year: "numeric",
              month: "long",
              day: "numeric",
              hour: "2-digit",
              minute: "2-digit",
            })}
          </span>
          <span>views {post.view_count}</span>
        </div>
      </div>

      {/* Content */}
      <div className="prose-invert max-w-none">
        <div className="text-gray-200 leading-relaxed whitespace-pre-wrap border-b border-gray-800 pb-8">
          {post.content}
        </div>
      </div>

      {/* Comments */}
      <section className="mt-8">
        <h2 className="text-lg font-semibold text-gray-100 mb-4">
          Comments ({comments.length})
        </h2>
        <CommentTree comments={comments} />
      </section>

      {/* Back */}
      <div className="mt-8 pt-4 border-t border-gray-800">
        <Link
          href="/"
          className="text-blue-400 hover:text-blue-300 text-sm"
        >
          Back to list
        </Link>
      </div>
    </article>
  );
}
