import AuthorBadge from "@/components/AuthorBadge";
import type { Comment } from "@/types";

function CommentNode({ comment, depth }: { comment: Comment; depth: number }) {
  return (
    <div
      className={depth > 0 ? "ml-6 border-l border-gray-700 pl-4" : ""}
    >
      <div className="py-3">
        <div className="flex items-center gap-2 mb-1 text-sm">
          <span className="font-medium text-gray-200">
            {comment.author_name}
          </span>
          <AuthorBadge type={comment.author_type} />
          <span className="text-gray-500">
            {new Date(comment.created_at).toLocaleDateString("ko-KR", {
              month: "short",
              day: "numeric",
              hour: "2-digit",
              minute: "2-digit",
            })}
          </span>
        </div>
        <p className="text-gray-300 whitespace-pre-wrap">{comment.content}</p>
      </div>
      {comment.replies?.map((reply) => (
        <CommentNode key={reply.id} comment={reply} depth={depth + 1} />
      ))}
    </div>
  );
}

export default function CommentTree({ comments }: { comments: Comment[] }) {
  if (comments.length === 0) {
    return <p className="text-gray-500 text-sm py-4">No comments yet.</p>;
  }

  return (
    <div className="divide-y divide-gray-800">
      {comments.map((comment) => (
        <CommentNode key={comment.id} comment={comment} depth={0} />
      ))}
    </div>
  );
}
