"use client";

import { useSyncExternalStore } from "react";
import {
  addMinimalEvidence,
  approveAndClose,
  approveReopen,
  assignComplaintToUnit,
  consumeHeldDraft,
  continueReopened,
  forwardEscalation,
  getAssignmentSnapshot,
  getComplaintById,
  getHeldDraftsSnapshot,
  handleEscalation,
  hasEscalationContextRequest,
  hasRejectContinuity,
  hasReopenContinuity,
  hasRequiredClosureHistory,
  hasRequiredEscalationHistory,
  hasRequiredRejectHistory,
  holdIntakeDraft,
  latestRejectHistory,
  listActiveCasesByCustomerRef,
  listClosedCasesByCustomerRef,
  listHeldDrafts,
  listOfficerAssigned,
  listPendingReopen,
  listPendingReview,
  listNewEscalations,
  listSlaAtRisk,
  listUnassigned,
  recordProgress,
  registerIntake,
  rejectReopen,
  rejectReview,
  requestEscalationContext,
  requestReopen,
  saveCorrection,
  saveFollowUp,
  searchCustomers,
  startHandling,
  submitEscalationContext,
  submitForReview,
  subscribeAssignmentRepo,
  type AddEvidenceError,
  type AddEvidenceResult,
  type ApproveCloseError,
  type ApproveCloseResult,
  type ApproveReopenError,
  type ApproveReopenResult,
  type AssignError,
  type AssignResult,
  type ContinueReopenedError,
  type ContinueReopenedResult,
  type ForwardEscalationError,
  type ForwardEscalationResult,
  type HandleEscalationError,
  type HandleEscalationResult,
  type HoldIntakeError,
  type HoldIntakeResult,
  type IntakeFormInput,
  type MockComplaint,
  type MockHeldDraft,
  type RecordProgressError,
  type RecordProgressResult,
  type RegisterIntakeError,
  type RegisterIntakeResult,
  type RejectReopenError,
  type RejectReopenResult,
  type RejectReviewError,
  type RejectReviewResult,
  type RequestEscalationContextError,
  type RequestEscalationContextResult,
  type RequestReopenError,
  type RequestReopenResult,
  type SaveCorrectionError,
  type SaveCorrectionResult,
  type SaveFollowUpError,
  type SaveFollowUpResult,
  type StartHandlingError,
  type StartHandlingResult,
  type SubmitEscalationContextError,
  type SubmitEscalationContextResult,
  type SubmitForReviewError,
  type SubmitForReviewResult,
} from "./assignmentRepository";

function getServerSnapshot(): readonly MockComplaint[] {
  return [];
}

function getHeldServerSnapshot(): readonly MockHeldDraft[] {
  return [];
}

export function useAssignmentRepository() {
  const snapshot = useSyncExternalStore(
    subscribeAssignmentRepo,
    getAssignmentSnapshot,
    getServerSnapshot,
  );

  const heldSnapshot = useSyncExternalStore(
    subscribeAssignmentRepo,
    getHeldDraftsSnapshot,
    getHeldServerSnapshot,
  );

  return {
    complaints: snapshot,
    heldDrafts: heldSnapshot,
    unassigned: listUnassigned(),
    pendingReview: listPendingReview(),
    pendingReopen: listPendingReopen(),
    newEscalations: listNewEscalations(),
    slaAtRisk: listSlaAtRisk(),
    officerAssigned: listOfficerAssigned(),
    getById: (id: string): MockComplaint | undefined => getComplaintById(id),
    searchCustomers,
    listActiveCasesByCustomerRef,
    listClosedCasesByCustomerRef,
    listHeldDrafts,
    assign: (
      complaintId: string,
      unitId: string,
    ): AssignResult | AssignError => assignComplaintToUnit(complaintId, unitId),
    startHandling: (
      complaintId: string,
    ): StartHandlingResult | StartHandlingError => startHandling(complaintId),
    recordProgress: (
      complaintId: string,
      text: string,
    ): RecordProgressResult | RecordProgressError =>
      recordProgress(complaintId, text),
    registerIntake: (
      input: IntakeFormInput,
    ): RegisterIntakeResult | RegisterIntakeError => registerIntake(input),
    holdIntakeDraft: (
      input: Parameters<typeof holdIntakeDraft>[0],
    ): HoldIntakeResult | HoldIntakeError => holdIntakeDraft(input),
    consumeHeldDraft,
    saveFollowUp: (
      complaintId: string,
      text: string,
    ): SaveFollowUpResult | SaveFollowUpError =>
      saveFollowUp(complaintId, text),
    submitForReview: (
      complaintId: string,
      resolutionSummary: string,
    ): SubmitForReviewResult | SubmitForReviewError =>
      submitForReview(complaintId, resolutionSummary),
    addMinimalEvidence: (
      complaintId: string,
      fileName: string,
    ): AddEvidenceResult | AddEvidenceError =>
      addMinimalEvidence(complaintId, fileName),
    approveAndClose: (
      complaintId: string,
    ): ApproveCloseResult | ApproveCloseError => approveAndClose(complaintId),
    rejectReview: (
      complaintId: string,
      reason: string,
    ): RejectReviewResult | RejectReviewError =>
      rejectReview(complaintId, reason),
    saveCorrection: (
      complaintId: string,
      resolutionSummary: string,
    ): SaveCorrectionResult | SaveCorrectionError =>
      saveCorrection(complaintId, resolutionSummary),
    requestReopen: (
      complaintId: string,
      reason: string,
    ): RequestReopenResult | RequestReopenError =>
      requestReopen(complaintId, reason),
    approveReopen: (
      complaintId: string,
    ): ApproveReopenResult | ApproveReopenError => approveReopen(complaintId),
    rejectReopen: (
      complaintId: string,
      reason: string,
    ): RejectReopenResult | RejectReopenError =>
      rejectReopen(complaintId, reason),
    continueReopened: (
      complaintId: string,
    ): ContinueReopenedResult | ContinueReopenedError =>
      continueReopened(complaintId),
    requestEscalationContext: (
      complaintId: string,
    ): RequestEscalationContextResult | RequestEscalationContextError =>
      requestEscalationContext(complaintId),
    submitEscalationContext: (
      complaintId: string,
      contextPackage: string,
    ): SubmitEscalationContextResult | SubmitEscalationContextError =>
      submitEscalationContext(complaintId, contextPackage),
    handleEscalation: (
      complaintId: string,
    ): HandleEscalationResult | HandleEscalationError =>
      handleEscalation(complaintId),
    forwardEscalation: (
      complaintId: string,
      reason: string,
    ): ForwardEscalationResult | ForwardEscalationError =>
      forwardEscalation(complaintId, reason),
    hasRejectContinuity,
    hasReopenContinuity,
    hasEscalationContextRequest,
    latestRejectHistory,
    hasRequiredRejectHistory,
    hasRequiredClosureHistory,
    hasRequiredEscalationHistory,
  };
}
