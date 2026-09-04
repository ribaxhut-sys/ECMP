import { describe, expect, it } from "vitest";
import {
  FOUNDATION_RETIRED_CASES_HREF,
  FOUNDATION_RETIRED_LIST_HREF,
} from "./foundationRetiredRedirect";

describe("DEC-026 M-026-1 Foundation retired doors", () => {
  it("sends leftover Foundation list/detail bookmarks to the CM list", () => {
    expect(FOUNDATION_RETIRED_LIST_HREF).toBe("/complaints");
  });

  it("sends leftover assign/resolve/queue Mode A doors to Case inbox", () => {
    expect(FOUNDATION_RETIRED_CASES_HREF).toBe("/complaints/cm/cases");
  });
});
