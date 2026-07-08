import type { GenerationResult } from "@/shared/types";

export interface ResultTab {
  label: string;
  badge?: number;
  result: GenerationResult;
}

const TAB_LABELS = [
  "Preview",
  "Screens",
  "States",
  "Design System",
  "Code",
  "Review",
  "Export",
] as const;

/**
 * GenerationResult 를 결과 뷰 탭 구성으로 매핑(순수).
 * 뱃지는 각 탭의 주요 카운트(Review=findings, Code=파일수, Screens=화면수).
 */
export function buildTabs(result: GenerationResult): ResultTab[] {
  const codeCount = result.code?.length ?? 0;
  const reviewCount = result.review?.length ?? 0;
  const screenCount = result.ux_plan?.screens?.length ?? 0;
  const badges: Partial<Record<(typeof TAB_LABELS)[number], number>> = {
    Screens: screenCount,
    Code: codeCount,
    Review: reviewCount,
  };
  return TAB_LABELS.map((label) => ({
    label,
    badge: badges[label],
    result,
  }));
}
