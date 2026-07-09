"use client";

import Link from "next/link";

interface StudioToolbarProps {
  onReset: () => void;
  hasResult: boolean;
}

/** 스튜디오 상단 툴바 — design.html 1456-1485. */
export function StudioToolbar({ onReset, hasResult }: StudioToolbarProps) {
  return (
    <div className="sticky top-14 z-30 border-b border-border bg-surface/70 backdrop-blur">
      <div className="flex h-12 items-center justify-between gap-4 px-4 md:px-6">
        <div className="flex min-w-0 items-center gap-3">
          <Link
            href="/"
            title="뒤로"
            className="rounded p-1.5 text-text-muted transition hover:bg-surface-alt hover:text-text"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M19 12H5M12 19l-7-7 7-7" />
            </svg>
          </Link>
          <div className="flex min-w-0 items-center gap-2">
            <span className="truncate font-serif text-[15px] text-text">
              {hasResult ? "디자인 스튜디오" : "새 디자인"}
            </span>
            <span className="rounded border border-border px-1.5 py-0.5 font-mono text-[10px] text-text-faint">
              {hasResult ? "결과" : "초안"}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className="hidden items-center gap-1 rounded border border-border px-2 py-1 font-mono text-[11px] text-text-muted sm:flex">
            <span className="h-1.5 w-1.5 rounded-full bg-success" />
            glm-5.2
          </div>
          <button
            onClick={onReset}
            className="flex items-center gap-1.5 rounded border border-border px-2.5 py-1.5 text-[12px] text-text-muted transition hover:border-text-muted hover:text-text"
          >
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 5v14M5 12h14" />
            </svg>
            새 대화
          </button>
        </div>
      </div>
    </div>
  );
}
