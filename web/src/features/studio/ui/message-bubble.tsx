"use client";

import type { Message } from "@/shared/types";

/** 사용자/에이전트 메시지 버블. design.html 1538-1641 포팅. */
export function MessageBubble({ message }: { message: Message }) {
  if (message.role === "user") {
    return (
      <div className="flex justify-end">
        <div className="max-w-[85%] rounded-lg rounded-tr-sm bg-text px-3.5 py-2.5 text-[13.5px] leading-relaxed text-bg">
          {message.content}
        </div>
      </div>
    );
  }
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <div className="flex h-6 w-6 items-center justify-center rounded-md border border-border-strong bg-surface">
          <div className="h-2 w-2 rounded-sm bg-accent" />
        </div>
        <span className="text-[12px] font-medium text-text">DevCanvas</span>
      </div>
      <p className="pl-8 text-[13px] leading-relaxed text-text-soft">{message.content}</p>
      {message.steps.length > 0 && <WorkSteps steps={message.steps} />}
    </div>
  );
}

/** 에이전트 작업 단계(완료 표시). design.html 1602-1613. */
function WorkSteps({ steps }: { steps: string[] }) {
  return (
    <div className="mt-1 pl-8">
      <div className="overflow-hidden rounded-md border border-border bg-surface">
        <div className="flex items-center justify-between border-b border-border px-3 py-1.5 font-mono text-[10px] uppercase text-text-faint">
          <span>작업 단계</span>
          <span className="text-success">{steps.length}/{steps.length} 완료</span>
        </div>
        <div className="space-y-0.5 px-3 py-2 font-mono text-[11px] leading-relaxed text-text-muted">
          {steps.map((s) => (
            <div key={s} className="diff-add -mx-2 px-2">
              + {s}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
