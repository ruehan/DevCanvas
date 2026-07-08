"use client";

import { SandpackProvider, SandpackLayout, SandpackPreview } from "@codesandbox/sandpack-react";
import type { ScreenLayout, ScreenState } from "@/shared/types";
import { buildSandpackFiles } from "@/features/preview/model";

interface SandpackPreviewViewProps {
  layout: ScreenLayout;
  state?: ScreenState;
}

/**
 * Sandpack 자급자족 프리뷰 (ADR-0015). SSR 불가 → next/dynamic ssr:false 로 로드.
 */
export function SandpackPreviewView({ layout, state }: SandpackPreviewViewProps) {
  const files = buildSandpackFiles(layout, state);
  return (
    <SandpackProvider template="react" files={files} theme="light">
      <SandpackLayout style={{ height: 400 }}>
        <SandpackPreview showOpenInCodeSandbox={false} />
      </SandpackLayout>
    </SandpackProvider>
  );
}
