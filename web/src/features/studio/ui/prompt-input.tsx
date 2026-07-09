"use client";

import { useState } from "react";

interface PromptInputProps {
  onSubmit: (prompt: string) => void;
  disabled?: boolean;
  placeholder?: string;
  rows?: number;
}

/** 하단 sticky 프롬프트 입력. ⏎ 전송 · ⇧⏎ 줄바꿈. design.html 1520-1531/1632-1643. */
export function PromptInput({
  onSubmit,
  disabled,
  placeholder = "예: 고객 관리 관리자 페이지를 만들어줘. 결제 상태 필터와 상세 보기 포함.",
  rows = 3,
}: PromptInputProps) {
  const [value, setValue] = useState("");

  function submit() {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSubmit(trimmed);
    setValue("");
  }

  return (
    <div className="shrink-0 border-t border-border bg-surface p-3">
      <div className="rounded-lg border border-border-strong bg-bg-soft transition focus-within:border-accent">
        <textarea
          rows={rows}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              submit();
            }
          }}
          placeholder={placeholder}
          disabled={disabled}
          className="w-full resize-none bg-transparent px-3.5 py-3 text-[13.5px] text-text placeholder:text-text-faint focus:outline-none disabled:text-text-faint"
        />
        <div className="flex items-center justify-between px-3 pb-2.5">
          <span className="font-mono text-[11px] text-text-faint">⏎ 전송 · ⇧⏎ 줄바꿈</span>
          <button
            onClick={submit}
            disabled={disabled || !value.trim()}
            className="flex items-center gap-1.5 rounded-md bg-accent px-3 py-1.5 text-[12px] font-medium text-white transition hover:bg-accent-hover disabled:opacity-50"
          >
            전송
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4">
              <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
