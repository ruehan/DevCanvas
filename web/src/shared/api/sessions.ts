import { env } from "@/shared/config";
import type { PostMessageResponse, Session } from "@/shared/types";

/** POST /sessions — 새 세션 생성. */
export async function createSession(base?: string): Promise<{ id: string }> {
  const url = `${base ?? env.apiBaseUrl}/sessions`;
  const res = await fetch(url, { method: "POST" });
  if (!res.ok) throw new Error(`세션 생성 실패: ${res.status} ${res.statusText}`);
  return res.json() as Promise<{ id: string }>;
}

/** POST /sessions/{id}/messages — 메시지 전송(첫 턴=전체 파이프라인, 이후=편집). */
export async function postSessionMessage(
  sessionId: string,
  prompt: string,
  base?: string,
): Promise<PostMessageResponse> {
  const url = `${base ?? env.apiBaseUrl}/sessions/${sessionId}/messages`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt }),
  });
  if (!res.ok) throw new Error(`메시지 전송 실패: ${res.status} ${res.statusText}`);
  return res.json() as Promise<PostMessageResponse>;
}

/** GET /sessions/{id} — 세션 상태. */
export async function getSession(sessionId: string, base?: string): Promise<Session> {
  const url = `${base ?? env.apiBaseUrl}/sessions/${sessionId}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`세션 조회 실패: ${res.status} ${res.statusText}`);
  return res.json() as Promise<Session>;
}
