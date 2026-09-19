/** Pure form state/validation for Buat Pengaduan Internal. */
import type { InternalCategory, InternalPriority } from "./types";

export interface InternalComplaintFormValues {
  title: string;
  /** Optional Handling Unit (Cabang ↔ Pusat). Empty = stay at owner unit. */
  destinationUnitId: string;
  /**
   * Required when destinationUnitId is set AND the actor is a Pusat
   * Agent-family (no complaints:assign) — becomes a transfer request.
   * Cabang create always goes to Pusat without this field.
   */
  requestReason: string;
  category: InternalCategory | "";
  /** Optional Batch-1 Aggregate complaint id (UUID). */
  relatedComplaintId: string;
  priority: InternalPriority;
  description: string;
  chronology: string;
  impact: string;
}

export function defaultInternalComplaintForm(): InternalComplaintFormValues {
  return {
    title: "",
    destinationUnitId: "",
    requestReason: "",
    category: "",
    relatedComplaintId: "",
    priority: "MEDIUM",
    description: "",
    chronology: "",
    impact: "",
  };
}

export type InternalComplaintFormErrors = Partial<
  Record<keyof InternalComplaintFormValues, string>
>;

export function validateInternalComplaintForm(
  values: InternalComplaintFormValues,
  options?: {
    canAssign?: boolean;
    relatedUnresolved?: boolean;
    /** Pusat Agent picking a cabang destination — not used for cabang→Pusat create. */
    requireRequestReason?: boolean;
  },
): InternalComplaintFormErrors {
  const errors: InternalComplaintFormErrors = {};
  if (!values.title.trim()) errors.title = "titleRequiredError";
  if (!values.category) errors.category = "categoryRequiredError";
  if (!values.description.trim()) errors.description = "descriptionRequiredError";
  const requireReason = options?.requireRequestReason ?? false;
  if (requireReason && values.destinationUnitId.trim() && !values.requestReason.trim()) {
    errors.requestReason = "requestReasonRequiredError";
  }
  if (options?.relatedUnresolved) {
    errors.relatedComplaintId = "relatedComplaintNotFoundError";
  }
  return errors;
}

export function isInternalComplaintFormValid(
  errors: InternalComplaintFormErrors,
): boolean {
  return Object.keys(errors).length === 0;
}
