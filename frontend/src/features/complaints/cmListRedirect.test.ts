import { describe, expect, it } from "vitest";
import { cmCompatListRedirectHref } from "./cmListRedirect";

describe("cmCompatListRedirectHref", () => {
  it("sends bare /complaints/cm to the CM list", () => {
    expect(cmCompatListRedirectHref({})).toBe("/complaints");
  });

  it("preserves keyword and status so Header search bookmarks still work", () => {
    expect(
      cmCompatListRedirectHref({
        keyword: "UNIT-2608-0001",
        status: "OPEN",
      }),
    ).toBe("/complaints?keyword=UNIT-2608-0001&status=OPEN");
  });
});
