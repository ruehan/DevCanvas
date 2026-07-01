import { describe, it, expect } from "vitest";
import { APP_NAME } from "./index";

describe("shared/lib", () => {
  it("APP_NAME이 DevCanvas다", () => {
    expect(APP_NAME).toBe("DevCanvas");
  });
});
