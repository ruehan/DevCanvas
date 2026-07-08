"use client";

import { useState } from "react";
import type { GenerationRequest, ScreenType, Tone } from "@/shared/types/schemas";

const SCREEN_TYPES: ScreenType[] = ["admin", "dashboard", "internal_tool"];
const TONES: Tone[] = ["b2b", "minimal", "enterprise", "startup", "friendly"];

interface GenerationFormProps {
  onSubmit: (request: GenerationRequest) => void;
  disabled?: boolean;
}

export function GenerationForm({ onSubmit, disabled }: GenerationFormProps) {
  const [prompt, setPrompt] = useState("");
  const [screenType, setScreenType] = useState<ScreenType>("dashboard");
  const [serviceType, setServiceType] = useState("SaaS");
  const [role, setRole] = useState("관리자");
  const [dataFields, setDataFields] = useState("");
  const [tone, setTone] = useState<Tone>("b2b");
  const [stack, setStack] = useState("Next.js + Tailwind + shadcn/ui");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    onSubmit({
      prompt,
      screen_type: screenType,
      service_type: serviceType,
      role,
      data_fields: dataFields
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean),
      tone,
      stack,
    });
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4" aria-label="UI 생성 요청 폼">
      <label className="block">
        <span className="block text-sm font-medium">프롬프트</span>
        <textarea
          className="mt-1 w-full rounded border p-2"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="예: B2B SaaS 관리자 페이지. 고객 목록, 결제 상태, 검색, 필터..."
          aria-label="프롬프트"
          rows={4}
          required
        />
      </label>

      <div className="grid grid-cols-2 gap-4">
        <label className="block">
          <span className="block text-sm font-medium">화면 유형</span>
          <select
            className="mt-1 w-full rounded border p-2"
            value={screenType}
            onChange={(e) => setScreenType(e.target.value as ScreenType)}
            aria-label="화면 유형"
          >
            {SCREEN_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </label>

        <label className="block">
          <span className="block text-sm font-medium">디자인 톤</span>
          <select
            className="mt-1 w-full rounded border p-2"
            value={tone}
            onChange={(e) => setTone(e.target.value as Tone)}
            aria-label="디자인 톤"
          >
            {TONES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </label>

        <label className="block">
          <span className="block text-sm font-medium">서비스 유형</span>
          <input
            className="mt-1 w-full rounded border p-2"
            value={serviceType}
            onChange={(e) => setServiceType(e.target.value)}
            aria-label="서비스 유형"
          />
        </label>

        <label className="block">
          <span className="block text-sm font-medium">사용자 역할</span>
          <input
            className="mt-1 w-full rounded border p-2"
            value={role}
            onChange={(e) => setRole(e.target.value)}
            aria-label="사용자 역할"
          />
        </label>
      </div>

      <label className="block">
        <span className="block text-sm font-medium">데이터 필드(쉼표 구분)</span>
        <input
          className="mt-1 w-full rounded border p-2"
          value={dataFields}
          onChange={(e) => setDataFields(e.target.value)}
          placeholder="고객명, 결제 상태, 계약일"
          aria-label="데이터 필드"
        />
      </label>

      <label className="block">
        <span className="block text-sm font-medium">출력 스택</span>
        <input
          className="mt-1 w-full rounded border p-2"
          value={stack}
          onChange={(e) => setStack(e.target.value)}
          aria-label="출력 스택"
        />
      </label>

      <button
        type="submit"
        disabled={disabled}
        className="rounded bg-blue-600 px-4 py-2 text-white disabled:opacity-50"
      >
        {disabled ? "생성 중..." : "생성"}
      </button>
    </form>
  );
}
