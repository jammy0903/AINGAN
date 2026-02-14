"use client";

import { useEffect } from "react";
import { recordView } from "@/lib/api";

export default function ViewCounter({ postId }: { postId: string }) {
  useEffect(() => {
    // 클라이언트 로드 후 즉시 view 기록
    const recordViewAsync = async () => {
      try {
        await recordView(postId);
        console.log(`[ViewCounter] recorded view for post ${postId}`);
      } catch (error) {
        console.error(`[ViewCounter] Failed to record view:`, error);
      }
    };

    recordViewAsync();
  }, [postId]);

  return null;
}
