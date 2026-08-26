import { describe, expect, it } from "vitest";
import {
  customerLabelForId,
  customerListLabel,
  looksLikeUuid,
} from "./customerListLabels";

describe("customerListLabel", () => {
  it("keeps name and number separate when they differ", () => {
    expect(customerListLabel("Siti Rahayu", "WP-9901")).toEqual({
      name: "Siti Rahayu",
      number: "WP-9901",
    });
  });

  it("does not duplicate the name as the number", () => {
    expect(customerListLabel("Siti Rahayu", "Siti Rahayu")).toEqual({
      name: "Siti Rahayu",
      number: null,
    });
  });
});

describe("customerLabelForId", () => {
  it("returns the mapped taxpayer name", () => {
    expect(
      customerLabelForId(
        "cust-1",
        { "cust-1": { name: "Siti Rahayu", number: "WP-9901" } },
        "—",
      ),
    ).toEqual({ name: "Siti Rahayu", number: "WP-9901" });
  });

  it("hides unresolved UUID identifiers", () => {
    expect(
      looksLikeUuid("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"),
    ).toBe(true);
    expect(
      customerLabelForId("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee", {}, "—"),
    ).toEqual({ name: "—", number: null });
  });
});
