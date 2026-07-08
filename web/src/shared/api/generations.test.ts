import { describe, it, expect, vi, afterEach, beforeEach } from "vitest";
import { createGeneration } from "./generations";
import type { GenerationRequest } from "@/shared/types/schemas";

describe("shared/api/generations", () => {
  beforeEach(() => {
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "http://test-api");
  });
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.restoreAllMocks();
  });

  it("POST /generations 으로 요청하고 결과를 반환한다", async () => {
    const mockResult = { input: { prompt: "x" }, code: [] };
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue({ ok: true, json: async () => mockResult } as Response);

    const req: GenerationRequest = {
      prompt: "고객 관리 페이지",
      screen_type: "admin",
      service_type: "SaaS",
      role: "관리자",
      data_fields: ["고객명"],
      tone: "b2b",
      stack: "Next.js + Tailwind",
    };
    const result = await createGeneration(req);

    expect(fetchMock).toHaveBeenCalledOnce();
    const call = fetchMock.mock.calls[0];
    expect(call).toBeDefined();
    const [url, init] = call!;
    expect(url).toBe("http://test-api/generations");
    expect(init?.method).toBe("POST");
    expect(JSON.parse((init?.body as string) ?? "{}")).toEqual(req);
    expect(result).toEqual(mockResult);
  });

  it("응답이 ok 가 아니면 에러를 던진다", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: false,
      status: 500,
      statusText: "Server Error",
    } as Response);

    await expect(
      createGeneration({ prompt: "x" } as GenerationRequest),
    ).rejects.toThrow();
  });

  it("base 인자로 기본 URL 을 덮어쓸 수 있다", async () => {
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue({ ok: true, json: async () => ({}) } as Response);

    await createGeneration({ prompt: "x" } as GenerationRequest, "http://other");
    const call = fetchMock.mock.calls[0];
    expect(call![0]).toBe("http://other/generations");
  });
});
