import { describe, it, expect } from "vitest";
import config from "./tailwind.config";

describe("tailwind config (디자인 시스템 — ADR-0019)", () => {
  it("warm neutral 팔레트를 정의한다", () => {
    const colors = config.theme?.extend?.colors as Record<string, unknown>;
    expect(colors).toBeDefined();
    expect(colors.bg).toBe("#FAF9F5");
    expect(colors.surface).toBe("#FFFFFF");
    // accent 는 객체(DEFAULT/hover/soft)
    const accent = colors.accent as { DEFAULT: string; hover: string };
    expect(accent.DEFAULT).toBe("#C96442");
    expect(accent.hover).toBe("#B5533A");
  });

  it("GmarketSans 와 JetBrains Mono 폰트 매핑", () => {
    const fontFamily = config.theme?.extend?.fontFamily as {
      sans: string[];
      mono: string[];
    };
    expect(fontFamily.sans).toContain("GmarketSans");
    expect(fontFamily.mono[0]).toBe("var(--font-jbmono)");
  });
});
