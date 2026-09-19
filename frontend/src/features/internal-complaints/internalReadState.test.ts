import { describe, expect, it } from "vitest";
import { internalTicketNumberClass } from "./internalReadState";

describe("internalTicketNumberClass", () => {
  it("uses unread typography only when isRead is false", () => {
    expect(internalTicketNumberClass(false, "bold", "regular")).toBe("bold");
    expect(internalTicketNumberClass(true, "bold", "regular")).toBe("regular");
    expect(internalTicketNumberClass(undefined, "bold", "regular")).toBe(
      "regular",
    );
  });
});
