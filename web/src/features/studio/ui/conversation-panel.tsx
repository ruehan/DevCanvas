"use client";

import type { Message } from "@/shared/types";
import { MessageBubble } from "./message-bubble";
import { LoadingAgent } from "./loading-agent";
import { PromptInput } from "./prompt-input";

const EXAMPLE_PROMPTS: { title: string; desc: string; prompt: string }[] = [
  {
    title: "정기결제 SaaS 관리자 페이지",
    desc: "MRR 대시보드, 구독자 관리, 환불 이력 포함",
    prompt: "정기결제 SaaS 관리자 페이지를 만들어줘. MRR 대시보드, 구독자 관리, 환불 이력 포함.",
  },
  {
    title: "채용 플랫폼 공고 목록",
    desc: "필터 사이드바, 카드형 리스트, 상세 모달",
    prompt: "채용 플랫폼 공고 목록을 만들어줘. 필터 사이드바, 카드형 리스트, 상세 모달 포함.",
  },
  {
    title: "이커머스 주문 관리",
    desc: "주문 상태별 탭, 검색, 일괄 처리",
    prompt: "이커머스 주문 관리 페이지를 만들어줘. 주문 상태별 탭, 검색, 일괄 처리 포함.",
  },
];

interface ConversationPanelProps {
  phase: "empty" | "loading" | "ready";
  messages: Message[];
  pendingPrompt: string | null;
  error: string | null;
  onSubmit: (prompt: string) => void;
}

/** 좌측 대화 패널 — design.html 1490-1645 포팅, phase 동기. */
export function ConversationPanel({
  phase,
  messages,
  pendingPrompt,
  error,
  onSubmit,
}: ConversationPanelProps) {
  return (
    <aside className="flex min-h-0 flex-col overflow-hidden border-r border-border bg-bg">
      {/* EMPTY */}
      {phase === "empty" && (
        <div className="flex min-h-0 flex-1 flex-col">
          <div className="flex min-h-0 flex-1 flex-col items-center justify-center overflow-y-auto px-8 py-10 text-center">
            <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-md border border-border-strong bg-surface">
              <div className="h-4 w-4 rounded-sm bg-accent" />
            </div>
            <h2 className="mb-2 font-serif text-[24px] text-text">무엇을 만들까요?</h2>
            <p className="max-w-[320px] text-[13px] leading-relaxed text-text-muted">
              프롬프트로 시작하세요. 화면 구조, 상태별 UI, 코드까지 만들어드립니다.
            </p>
            {error && (
              <p role="alert" className="mt-4 text-[12px] text-danger">
                오류: {error}
              </p>
            )}
            <div className="mt-8 w-full max-w-[420px] space-y-2 text-left">
              <div className="mb-2 font-mono text-[10px] uppercase tracking-wider text-text-faint">
                예시 프롬프트
              </div>
              {EXAMPLE_PROMPTS.map((ex) => (
                <button
                  key={ex.title}
                  onClick={() => onSubmit(ex.prompt)}
                  className="chip w-full rounded-md border border-border bg-surface px-3 py-2.5 text-left text-[13px] text-text transition"
                >
                  <span className="block text-text">{ex.title}</span>
                  <span className="mt-0.5 block text-[11px] text-text-muted">{ex.desc}</span>
                </button>
              ))}
            </div>
          </div>
          <PromptInput onSubmit={onSubmit} />
        </div>
      )}

      {/* LOADING */}
      {phase === "loading" && (
        <div className="flex min-h-0 flex-1 flex-col">
          <div className="flex-1 space-y-5 overflow-y-auto px-5 py-6">
            <div className="flex justify-end">
              <div className="max-w-[85%] rounded-lg rounded-tr-sm bg-text px-3.5 py-2.5 text-[13.5px] leading-relaxed text-bg">
                {pendingPrompt ?? ""}
              </div>
            </div>
            <LoadingAgent prompt={pendingPrompt ?? ""} />
          </div>
          <PromptInput onSubmit={onSubmit} disabled rows={2} placeholder="생성 중... 잠시만 기다려주세요." />
        </div>
      )}

      {/* READY */}
      {phase === "ready" && (
        <div className="flex min-h-0 flex-1 flex-col">
          <div className="flex-1 space-y-5 overflow-y-auto px-5 py-6">
            {messages.map((m, i) => (
              <MessageBubble key={i} message={m} />
            ))}
            {error && (
              <p role="alert" className="text-[12px] text-danger">
                오류: {error}
              </p>
            )}
          </div>
          <PromptInput
            onSubmit={onSubmit}
            rows={2}
            placeholder="후속 수정 요청 입력... (예: 버튼 더 둥글게, 모바일은 카드형으로)"
          />
        </div>
      )}
    </aside>
  );
}
