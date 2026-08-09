/** Pure form state/validation for Buat Pengaduan Internal. */
import type { InternalCategory, InternalPriority } from "./types";

export interface InternalComplaintFormValues {
  title: string;
  /** Optional initial transfer destination (Branch.code). Empty = stay at owner unit. */
  destinationUnitId: string;
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
): InternalComplaintFormErrors {
  const errors: InternalComplaintFormErrors = {};
  if (!values.title.trim()) errors.title = "titleRequiredError";
  if (!values.category) errors.category = "categoryRequiredError";
  if (!values.description.trim()) errors.description = "descriptionRequiredError";
  return errors;
}

export function isInternalComplaintFormValid(
  errors: InternalComplaintFormErrors,
): boolean {
  return Object.keys(errors).length === 0;
}
