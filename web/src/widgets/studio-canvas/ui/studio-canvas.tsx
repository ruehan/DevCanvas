"use client";

import type { GenerationResult } from "@/shared/types";
import { ResultViewer } from "@/widgets/result-viewer";

interface StudioCanvasProps {
  phase: "empty" | "loading" | "ready";
  result: GenerationResult | null;
}

/** 우측 캔버스 — design.html 1647-1700. 빈/로딩(스켈레톤)/결과(기존 ResultViewer 재사용). */
export function StudioCanvas({ phase, result }: StudioCanvasProps) {
  return (
    <section className="flex min-h-0 min-w-0 flex-col bg-bg-soft">
      {phase === "empty" && (
        <div className="flex h-full flex-col items-center justify-center p-6 text-center">
          <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-lg border border-dashed border-border-strong bg-surface">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#9A958B" strokeWidth="1.5">
              <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7z" />
              <circle cx="12" cy="12" r="3" />
            </svg>
          </div>
          <h3 className="mb-1.5 font-serif text-[20px] text-text">프롬프트로 시작하세요</h3>
          <p className="max-w-[280px] text-[12.5px] leading-relaxed text-text-muted">
            좌측에 프롬프트를 입력하면
            <br />
            여기에 실시간 결과물이 표시됩니다.
          </p>
        </div>
      )}

      {phase === "loading" && <CanvasSkeleton />}

      {phase === "ready" && result && (
        <div className="min-h-0 flex-1 overflow-auto">
          <ResultViewer result={result} />
        </div>
      )}
    </section>
  );
}

/** 로딩 스켈레톤 — design.html 1685-1699. */
function CanvasSkeleton() {
  return (
    <div className="h-full p-4 md:p-6">
      <div className="mx-auto max-w-[900px]">
        <div className="mb-4 flex items-center justify-between">
          <div className="space-y-2">
            <div className="skeleton h-5 w-48 rounded" />
            <div className="skeleton h-3 w-32 rounded" />
          </div>
          <div className="flex gap-2">
            <div className="skeleton h-7 w-16 rounded" />
            <div className="skeleton h-7 w-16 rounded" />
          </div>
        </div>
        <div className="overflow-hidden rounded-lg border border-border bg-surface">
          <div className="grid grid-cols-4 gap-3 border-b border-border px-4 py-2.5">
            <div className="skeleton h-3 rounded" />
            <div className="skeleton h-3 rounded" />
            <div className="skeleton h-3 rounded" />
            <div className="skeleton h-3 rounded" />
          </div>
          <div className="divide-y divide-border">
            {[0, 1, 2].map((i) => (
              <div key={i} className="grid grid-cols-4 gap-3 px-4 py-3">
                <div className="skeleton h-3 w-3/4 rounded" />
                <div className="skeleton h-3 w-1/2 rounded" />
                <div className="skeleton h-3 w-2/3 rounded" />
                <div className="skeleton h-5 w-14 rounded" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
