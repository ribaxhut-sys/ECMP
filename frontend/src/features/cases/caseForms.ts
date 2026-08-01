import type {
  AddCmCaseRequest,
  CloseCmCaseRequest,
  CreateCmCaseRequest,
  CmCaseCancelReason,
  CmCaseResolveAction,
  CmCaseStatus,
  ResolveCmCaseRequest,
  UpdateCmCaseStatusRequest,
} from "@/lib/api/cmCase";

export interface CreateCaseFormValues {
  caseType: string;
  category: string;
  subject: string;
  description: string;
  priority: string;
  destinationUnitId: string;
}

export type CreateCaseFieldErrors = Partial<
  Record<keyof CreateCaseFormValues, string>
>;

export function emptyCreateCaseForm(): CreateCaseFormValues {
  return {
    caseType: "",
    category: "",
    subject: "",
    description: "",
    priority: "MEDIUM",
    destinationUnitId: "",
  };
}

export const CASE_PRIORITY_OPTIONS = [
  { value: "LOW", label: "low" },
  { value: "MEDIUM", label: "medium" },
  { value: "HIGH", label: "high" },
  { value: "CRITICAL", label: "critical" },
] as const;

export const CANCEL_REASON_OPTIONS: { value: CmCaseCancelReason; label: string }[] =
  [
    { value: "DUPLICATE", label: "cancelReasonOptionDuplicate" },
    { value: "WRONG_INPUT", label: "cancelReasonOptionWrongInput" },
    { value: "CUSTOMER_CANCELLATION", label: "cancelReasonOptionCustomerCancellation" },
  ];

export function validateCreateCaseForm(
  values: CreateCaseFormValues,
): CreateCaseFieldErrors {
  const errors: CreateCaseFieldErrors = {};
  if (!values.caseType.trim()) errors.caseType = "caseTypeRequired";
  if (!values.subject.trim()) errors.subject = "subjectRequired";
  if (!values.description.trim()) errors.description = "descriptionRequired";
  if (!values.priority.trim()) errors.priority = "priorityRequired";
  return errors;
}

export function toCreateCaseRequest(
  complaintId: string,
  values: CreateCaseFormValues,
): CreateCmCaseRequest {
  const destinationUnitId = values.destinationUnitId.trim() || null;
  return {
    complaintId,
    caseType: values.caseType.trim(),
    category: values.category.trim() || null,
    subject: values.subject.trim(),
    description: values.description.trim(),
    priority: values.priority.trim(),
    destinationUnitId,
  };
}

export function toAddCaseRequest(
  values: CreateCaseFormValues,
): AddCmCaseRequest {
  const destinationUnitId = values.destinationUnitId.trim() || null;
  return {
    caseType: values.caseType.trim(),
    category: values.category.trim() || null,
    subject: values.subject.trim(),
    description: values.description.trim(),
    priority: values.priority.trim(),
    destinationUnitId,
  };
}

export interface UpdateStatusFormValues {
  toStatus: CmCaseStatus | "";
  destinationUnitId: string;
  cancelReason: CmCaseCancelReason | "";
  reason: string;
}

export type UpdateStatusFieldErrors = Partial<
  Record<keyof UpdateStatusFormValues, string>
>;

export function emptyUpdateStatusForm(
  defaults?: Partial<UpdateStatusFormValues>,
): UpdateStatusFormValues {
  return {
    toStatus: "",
    destinationUnitId: "",
    cancelReason: "",
    reason: "",
    ...defaults,
  };
}

export function validateUpdateStatusForm(
  values: UpdateStatusFormValues,
): UpdateStatusFieldErrors {
  const errors: UpdateStatusFieldErrors = {};
  if (!values.toStatus) errors.toStatus = "targetStatusRequired";
  if (values.toStatus === "ASSIGNED" && !values.destinationUnitId.trim()) {
    errors.destinationUnitId = "destinationUnitRequired";
  }
  if (values.toStatus === "CANCELLED") {
    if (!values.cancelReason) {
      errors.cancelReason = "cancelReasonRequired";
    }
    if (!values.reason.trim()) {
      errors.reason = "cancelReasonTextRequired";
    }
  }
  return errors;
}

export function toUpdateStatusRequest(
  values: UpdateStatusFormValues,
): UpdateCmCaseStatusRequest {
  return {
    toStatus: values.toStatus as CmCaseStatus,
    destinationUnitId: values.destinationUnitId.trim() || null,
    cancelReason: (values.cancelReason || null) as CmCaseCancelReason | null,
    reason: values.reason.trim() || null,
  };
}

export interface ResolveCaseFormValues {
  action: CmCaseResolveAction;
  comment: string;
  resolutionCode: string;
  summary: string;
  detail: string;
  rejectionReason: string;
}

export type ResolveCaseFieldErrors = Partial<
  Record<keyof ResolveCaseFormValues, string>
>;

export function emptyResolveCaseForm(): ResolveCaseFormValues {
  return {
    action: "ACCEPT",
    comment: "",
    resolutionCode: "",
    summary: "",
    detail: "",
    rejectionReason: "",
  };
}

export function validateResolveCaseForm(
  values: ResolveCaseFormValues,
): ResolveCaseFieldErrors {
  const errors: ResolveCaseFieldErrors = {};
  if (!values.comment.trim()) errors.comment = "commentRequired";
  if (values.action === "PROPOSE" || values.action === "ACCEPT") {
    if (!values.resolutionCode.trim()) {
      errors.resolutionCode = "resolutionCodeRequired";
    }
    if (!values.summary.trim()) errors.summary = "summaryRequired";
  }
  if (values.action === "REJECT" && !values.rejectionReason.trim()) {
    errors.rejectionReason = "rejectionReasonRequired";
  }
  return errors;
}

export function toResolveCaseRequest(
  values: ResolveCaseFormValues,
): ResolveCmCaseRequest {
  return {
    action: values.action,
    comment: values.comment.trim(),
    resolutionCode: values.resolutionCode.trim() || null,
    summary: values.summary.trim() || null,
    detail: values.detail.trim() || null,
    rejectionReason: values.rejectionReason.trim() || null,
  };
}

export interface CloseCaseFormValues {
  note: string;
}

export function emptyCloseCaseForm(): CloseCaseFormValues {
  return { note: "" };
}

export function toCloseCaseRequest(
  values: CloseCaseFormValues,
): CloseCmCaseRequest {
  return { note: values.note.trim() || null };
}
