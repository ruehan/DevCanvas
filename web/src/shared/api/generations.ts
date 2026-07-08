import { env } from "@/shared/config";
import type { GenerationRequest, GenerationResult } from "@/shared/types/schemas";

/**
 * POST /generations 호출. base 가 주어지면 env 기본값을 덮어쓴다.
 */
export async function createGeneration(
  request: GenerationRequest,
  base?: string,
): Promise<GenerationResult> {
  const url = `${base ?? env.apiBaseUrl}/generations`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!res.ok) {
    throw new Error(`생성 요청 실패: ${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<GenerationResult>;
}
