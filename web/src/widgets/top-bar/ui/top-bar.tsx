"use client";

import Link from "next/link";

interface TopBarProps {
  /** 현재 활성 뷰(네비 표시용). 기본 "landing". */
  active?: "landing" | "studio";
}

/** 상단 바 — 랜딩/스튜디오 공용 (ADR-0019, design.html 기반). */
export function TopBar({ active = "landing" }: TopBarProps) {
  return (
    <header className="sticky top-0 z-40 border-b border-border bg-bg/85 backdrop-blur">
      <div className="mx-auto flex h-14 max-w-[1400px] items-center justify-between px-6 md:px-10">
        <div className="flex items-center gap-8">
          <Link href="/" className="flex cursor-pointer items-center gap-2.5">
            <div className="flex h-7 w-7 items-center justify-center rounded-md border border-text/15 bg-surface">
              <div className="h-3 w-3 rounded-sm bg-accent" />
            </div>
            <span className="font-serif text-[19px] text-text">DevCanvas</span>
            <span className="rounded border border-border-strong px-1.5 py-0.5 font-mono text-2xs text-text-faint">
              v2
            </span>
          </Link>
          <nav className="hidden items-center gap-1 text-[13px] md:flex">
            <Link
              href="/"
              aria-selected={active === "landing"}
              className="rounded-md px-3 py-1.5 text-text-muted transition hover:bg-surface-alt hover:text-text aria-selected:text-text"
            >
              소개
            </Link>
            <Link
              href="/studio"
              aria-selected={active === "studio"}
              className="rounded-md px-3 py-1.5 text-text-muted transition hover:bg-surface-alt hover:text-text aria-selected:text-text"
            >
              스튜디오
            </Link>
            <a
              href="#"
              className="rounded-md px-3 py-1.5 text-text-muted transition hover:bg-surface-alt hover:text-text"
            >
              문서
            </a>
          </nav>
        </div>
        <div className="flex items-center gap-2">
          <a
            href="#"
            className="hidden items-center gap-1.5 rounded-md px-3 py-1.5 text-[13px] text-text-muted transition hover:bg-surface-alt hover:text-text md:inline-flex"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
              <path d="M9 19c-5 0-8-3-8-7s3-7 8-7c2 0 3 .5 4 1.5" />
              <path d="M15 5c5 0 8 3 8 7s-3 7-8 7c-2 0-3-.5-4-1.5" />
            </svg>
            공개 프로젝트
          </a>
          <Link
            href="/studio"
            className="rounded-md bg-text px-3.5 py-1.5 text-[13px] font-medium text-bg transition hover:bg-text-soft"
          >
            스튜디오 열기
          </Link>
        </div>
      </div>
    </header>
  );
}
