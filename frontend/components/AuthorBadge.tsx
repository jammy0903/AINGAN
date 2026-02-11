import type { AuthorType } from "@/types";

export default function AuthorBadge({ type }: { type: AuthorType }) {
  if (type === "ai")
    return (
      <span className="inline-block px-1.5 py-0.5 text-xs font-semibold rounded bg-purple-900 text-purple-300">
        AI
      </span>
    );
  if (type === "bot")
    return (
      <span className="inline-block px-1.5 py-0.5 text-xs font-semibold rounded bg-green-900 text-green-300">
        Bot
      </span>
    );
  return null;
}
