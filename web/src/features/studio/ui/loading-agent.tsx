"use client";

/** 로딩 중 에이전트 표시 — typing + 진행 표시. design.html 1542-1571. */
export function LoadingAgent({ prompt }: { prompt: string }) {
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <div className="flex h-6 w-6 items-center justify-center rounded-md border border-border-strong bg-surface">
          <div className="h-2 w-2 rounded-sm bg-accent" />
        </div>
        <span className="text-[12px] font-medium text-text">DevCanvas</span>
        <span className="typing">
          <span />
          <span />
          <span />
        </span>
      </div>
      <div className="mt-3 pl-8">
        <div className="relative h-1 overflow-hidden rounded-full bg-surface-alt progress-bar" />
        <p className="mt-2 text-[11px] text-text-faint">생성 중…</p>
      </div>
    </div>
  );
}
