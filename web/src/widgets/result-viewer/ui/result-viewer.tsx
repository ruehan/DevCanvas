"use client";

import { useState } from "react";
import type { GenerationResult } from "@/shared/types";
import { buildTabs } from "@/widgets/result-viewer/model";

interface ResultViewerProps {
  result: GenerationResult;
}

export function ResultViewer({ result }: ResultViewerProps) {
  const tabs = buildTabs(result);
  const [active, setActive] = useState(tabs[0]?.label ?? "Preview");
  const [selectedFile, setSelectedFile] = useState(result.code[0]?.path ?? "");

  return (
    <section aria-label="생성 결과" className="space-y-4">
      <nav className="flex flex-wrap gap-1 border-b" role="tablist">
        {tabs.map((tab) => (
          <button
            key={tab.label}
            role="tab"
            aria-selected={active === tab.label}
            onClick={() => setActive(tab.label)}
            className={
              "px-3 py-2 text-sm " +
              (active === tab.label ? "border-b-2 border-blue-600 font-medium" : "text-gray-600")
            }
          >
            {tab.label}
            {tab.badge !== undefined ? (
              <span className="ml-1 rounded bg-gray-200 px-1 text-xs">{tab.badge}</span>
            ) : null}
          </button>
        ))}
      </nav>

      {active === "Preview" && <PreviewPanel result={result} />}
      {active === "Screens" && <ScreensPanel result={result} />}
      {active === "States" && <StatesPanel result={result} />}
      {active === "Design System" && <DesignSystemPanel result={result} />}
      {active === "Code" && (
        <CodePanel
          result={result}
          selected={selectedFile}
          onSelect={setSelectedFile}
        />
      )}
      {active === "Review" && <ReviewPanel result={result} />}
      {active === "Export" && <ExportPanel result={result} />}
    </section>
  );
}

function PreviewPanel({ result }: { result: GenerationResult }) {
  // Sandpack 연동 전(ADR-0014): 페이지 코드를 텍스트로 표시
  const pages = result.code.filter((f) => f.path.endsWith("page.tsx"));
  return (
    <div className="text-sm text-gray-600">
      <p className="mb-2">
        미리보기는 Sandpack 연동(milestone #7) 전까지 페이지 코드로 대체 표시합니다.
      </p>
      <ul className="list-disc pl-5">
        {pages.map((p) => (
          <li key={p.path}>{p.path}</li>
        ))}
      </ul>
    </div>
  );
}

function ScreensPanel({ result }: { result: GenerationResult }) {
  return (
    <ul className="space-y-3">
      {result.ux_plan.screens.map((s) => (
        <li key={s.name} className="rounded border p-3">
          <div className="flex items-center gap-2">
            <span className="font-medium">{s.name}</span>
            <span className="rounded bg-gray-100 px-1 text-xs">{s.kind}</span>
          </div>
          <p className="text-sm text-gray-600">{s.purpose}</p>
          <p className="mt-1 text-xs text-gray-500">
            컴포넌트: {s.components.join(", ")}
          </p>
        </li>
      ))}
    </ul>
  );
}

function StatesPanel({ result }: { result: GenerationResult }) {
  const entries = Object.entries(result.ux_plan.states);
  return (
    <div className="space-y-4">
      {entries.map(([screen, state]) => (
        <div key={screen} className="rounded border p-3">
          <h4 className="font-medium">{screen}</h4>
          <table className="mt-2 w-full text-sm">
            <tbody>
              <StateRow label="Loading" value={state.loading} />
              <StateRow label="Empty" value={state.empty} />
              <StateRow label="Error" value={state.error} />
              <StateRow label="Permission" value={state.permission} />
              <StateRow label="Mobile" value={state.mobile} />
            </tbody>
          </table>
        </div>
      ))}
    </div>
  );
}

function StateRow({ label, value }: { label: string; value: string }) {
  return (
    <tr className="border-t">
      <th className="w-32 p-1 text-left text-xs text-gray-500">{label}</th>
      <td className="p-1">{value}</td>
    </tr>
  );
}

function DesignSystemPanel({ result }: { result: GenerationResult }) {
  const t = result.design_system.tokens;
  return (
    <div className="grid grid-cols-2 gap-4 text-sm">
      <TokenTable title="Colors" entries={t.colors} />
      <TokenTable title="Spacing" entries={t.spacing} />
      <TokenTable title="Radius" entries={t.radius} />
      <TokenTable title="Typography" entries={t.typography} />
      <TokenTable title="Shadows" entries={t.shadows} />
    </div>
  );
}

function TokenTable({ title, entries }: { title: string; entries: Record<string, string> }) {
  const rows = Object.entries(entries);
  return (
    <div>
      <h4 className="font-medium">{title}</h4>
      <table className="w-full">
        <tbody>
          {rows.map(([k, v]) => (
            <tr key={k} className="border-t">
              <td className="p-1 text-xs text-gray-500">{k}</td>
              <td className="p-1 font-mono text-xs">{v}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function CodePanel({
  result,
  selected,
  onSelect,
}: {
  result: GenerationResult;
  selected: string;
  onSelect: (path: string) => void;
}) {
  const file = result.code.find((f) => f.path === selected) ?? result.code[0];
  return (
    <div className="flex gap-3">
      <ul className="w-56 shrink-0 space-y-0.5 text-sm">
        {result.code.map((f) => (
          <li key={f.path}>
            <button
              onClick={() => onSelect(f.path)}
              className={
                "w-full truncate rounded px-2 py-1 text-left " +
                (selected === f.path ? "bg-blue-50 font-medium" : "hover:bg-gray-50")
              }
            >
              {f.path}
            </button>
          </li>
        ))}
      </ul>
      <pre className="flex-1 overflow-auto rounded bg-gray-50 p-3 text-xs">
        <code>{file?.content}</code>
      </pre>
    </div>
  );
}

function ReviewPanel({ result }: { result: GenerationResult }) {
  return (
    <ul className="space-y-2">
      {result.review.map((f, i) => (
        <li key={`${f.severity}-${f.category}-${i}`} className="rounded border p-2 text-sm">
          <span
            className={
              "mr-2 rounded px-1 text-xs " +
              (f.severity === "P1" ? "bg-red-100 text-red-700" : "bg-yellow-100 text-yellow-700")
            }
          >
            {f.severity}
          </span>
          <span className="text-gray-500">{f.category}</span>
          <p className="mt-1">{f.message}</p>
        </li>
      ))}
    </ul>
  );
}

function ExportPanel({ result }: { result: GenerationResult }) {
  return (
    <div className="space-y-3 text-sm">
      <div>
        <h4 className="font-medium">파일 트리</h4>
        <pre className="rounded bg-gray-50 p-2 text-xs">{result.handoff.file_tree.join("\n")}</pre>
      </div>
      <div>
        <h4 className="font-medium">설치 명령</h4>
        <pre className="rounded bg-gray-50 p-2 text-xs">
          {result.handoff.install_commands.join("\n") || "(없음)"}
        </pre>
      </div>
      <div>
        <h4 className="font-medium">TODO</h4>
        <ul className="list-disc pl-5">
          {result.handoff.todos.map((t, i) => (
            <li key={`${t}-${i}`}>{t}</li>
          ))}
        </ul>
      </div>
      <div>
        <h4 className="font-medium">구현 가이드</h4>
        <pre className="rounded bg-gray-50 p-2 text-xs whitespace-pre-wrap">
          {result.handoff.guide_md}
        </pre>
      </div>
    </div>
  );
}
