import { describe, expect, it } from "vitest";
import {
  classifyCustomerSearchKey,
  validateCustomerSearchKey,
} from "./customerSearchKey";

describe("customerSearchKey", () => {
  it("classifies name / id / phone", () => {
    expect(classifyCustomerSearchKey("Rina Uji")).toBe("name");
    expect(classifyCustomerSearchKey("3200000000000034")).toBe("id");
    expect(classifyCustomerSearchKey("083386093190")).toBe("phone");
    expect(classifyCustomerSearchKey("62 838 8609 3190")).toBe("phone");
  });

  it("enforces minimum lengths", () => {
    expect(validateCustomerSearchKey("").errorCode).toBe("empty");
    expect(validateCustomerSearchKey("Ab").errorCode).toBe("nameTooShort");
    expect(validateCustomerSearchKey("Ayu").ok).toBe(true);
    expect(validateCustomerSearchKey("32").errorCode).toBe("idTooShort");
    expect(validateCustomerSearchKey("32000000").ok).toBe(true);
    expect(validateCustomerSearchKey("0833").errorCode).toBe("phoneTooShort");
    expect(validateCustomerSearchKey("0833860931").ok).toBe(true);
  });
});
