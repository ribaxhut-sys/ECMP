"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type FormEvent,
} from "react";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  bookAppointment,
  checkInAppointment,
  completeAppointment,
  fetchAppointment,
  fetchComplaintEscalations,
  fetchUsers,
  markAppointmentNoShow,
  type UserRef,
} from "@/lib/api";
import type {
  Appointment,
  AppointmentCompletionResult,
  Escalation,
} from "@/lib/api/types";
import {
  Alert,
  Button,
  Card,
  CardBody,
  CardHeader,
  CardTitle,
  Input,
  Modal,
  Select,
  Textarea,
  Toast,
} from "@/shared/ui";

function formatDate(value: string | null | undefined): string {
  if (!value) return "—";
  try {
    return new Intl.DateTimeFormat(undefined, { dateStyle: "medium" }).format(
      new Date(`${value}T00:00:00`),
    );
  } catch {
    return value;
  }
}

function formatWhen(value: string | null | undefined): string {
  if (!value) return "—";
  try {
    return new Intl.DateTimeFormat(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(new Date(value));
  } catch {
    return value;
  }
}

function formatTime(value: string | null | undefined): string {
  if (!value) return "—";
  return value.length >= 5 ? value.slice(0, 5) : value;
}

function roleLabel(user: UserRef): string {
  return user.roleName?.trim() || user.roleCode?.trim() || "—";
}

function userOptionLabel(user: UserRef): string {
  return `${user.fullName} — ${roleLabel(user)}`;
}

function DetailField({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-0 space-y-1">
      <dt className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-wide text-ecmp-text-secondary">
        {label}
      </dt>
      <dd className="whitespace-pre-wrap break-words text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
        {value}
      </dd>
    </div>
  );
}

function pickApprovedEscalation(rows: Escalation[]): Escalation | null {
  return rows.find((row) => row.status === "APPROVED") ?? null;
}

const COMPLETION_RESULT_OPTIONS = [
  { value: "COMPLETED", label: "Completed" },
  { value: "PARTIALLY_COMPLETED", label: "Partially completed" },
];

export function AppointmentCard({
  complaintId,
  refreshKey = 0,
  onBooked,
}: {
  complaintId: string;
  refreshKey?: number;
  onBooked?: () => void;
}) {
  const { hasPermission } = useAuth();
  const canManage = hasPermission("escalations:review");
  const canComplete = hasPermission("appointments:complete");

  const [escalation, setEscalation] = useState<Escalation | null>(null);
  const [appointment, setAppointment] = useState<Appointment | null>(null);
  const [users, setUsers] = useState<UserRef[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [usersError, setUsersError] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [toastOpen, setToastOpen] = useState(false);
  const [toastTitle, setToastTitle] = useState("Appointment booked");
  const [toastDescription, setToastDescription] = useState(
    "Timeline updated. Escalation remains APPROVED.",
  );

  const [appointmentDate, setAppointmentDate] = useState("");
  const [startTime, setStartTime] = useState("09:00");
  const [endTime, setEndTime] = useState("10:00");
  const [engineerId, setEngineerId] = useState("");
  const [notes, setNotes] = useState("");

  const [checkInOpen, setCheckInOpen] = useState(false);
  const [checkInNotes, setCheckInNotes] = useState("");
  const [checkInError, setCheckInError] = useState<string | null>(null);
  const [checkingIn, setCheckingIn] = useState(false);

  const [completeOpen, setCompleteOpen] = useState(false);
  const [completionResult, setCompletionResult] =
    useState<AppointmentCompletionResult>("COMPLETED");
  const [completionNotes, setCompletionNotes] = useState("");
  const [completeError, setCompleteError] = useState<string | null>(null);
  const [completing, setCompleting] = useState(false);

  const [noShowOpen, setNoShowOpen] = useState(false);
  const [noShowReason, setNoShowReason] = useState("");
  const [noShowError, setNoShowError] = useState<string | null>(null);
  const [markingNoShow, setMarkingNoShow] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    setUsersError(null);
    try {
      const listRes = await fetchComplaintEscalations(complaintId);
      const approved = pickApprovedEscalation(listRes.data);
      setEscalation(approved);

      if (!approved) {
        setAppointment(null);
        return;
      }

      const summary = approved.activeAppointment ?? null;
      if (summary) {
        const detail = await fetchAppointment(summary.id);
        setAppointment(detail.data);
      } else {
        setAppointment(null);
      }

      if (canManage && !summary) {
        const usersRes = await fetchUsers({
          pageSize: 100,
          isActive: true,
        }).catch((err) => {
          setUsersError(
            err instanceof ApiError ? err.message : "Unable to load users.",
          );
          return null;
        });
        setUsers((usersRes?.data ?? []).filter((u) => u.isActive));
      } else {
        setUsers([]);
      }
    } catch (err) {
      setLoadError(
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Unable to load appointment.",
      );
      setEscalation(null);
      setAppointment(null);
    } finally {
      setLoading(false);
    }
  }, [canManage, complaintId]);

  useEffect(() => {
    void load();
  }, [load, refreshKey]);

  const engineerOptions = useMemo(
    () =>
      users.map((user) => ({
        value: user.id,
        label: userOptionLabel(user),
      })),
    [users],
  );

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (!escalation) return;

    const errors: Record<string, string> = {};
    if (!appointmentDate.trim()) errors.appointmentDate = "Date is required.";
    if (!startTime.trim()) errors.startTime = "Start time is required.";
    if (!endTime.trim()) errors.endTime = "End time is required.";
    if (!engineerId) errors.assignedEngineerId = "Engineer is required.";
    if (startTime && endTime && endTime <= startTime) {
      errors.endTime = "End time must be after start time.";
    }
    setFieldErrors(errors);
    if (Object.keys(errors).length > 0) return;

    setSubmitting(true);
    setSubmitError(null);
    try {
      const created = await bookAppointment(escalation.id, {
        appointmentDate,
        startTime,
        endTime,
        assignedEngineerId: engineerId,
        notes: notes.trim() || null,
      });
      const detail = await fetchAppointment(created.data.id);
      setAppointment(detail.data);
      setToastTitle("Appointment booked");
      setToastDescription("Timeline updated. Escalation remains APPROVED.");
      setToastOpen(true);
      onBooked?.();
      await load();
    } catch (err) {
      setSubmitError(
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Unable to book appointment.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  function openCheckIn() {
    setCheckInNotes("");
    setCheckInError(null);
    setCheckInOpen(true);
  }

  function closeCheckIn() {
    if (checkingIn) return;
    setCheckInOpen(false);
    setCheckInError(null);
  }

  async function confirmCheckIn() {
    if (!appointment) return;
    setCheckingIn(true);
    setCheckInError(null);
    try {
      await checkInAppointment(appointment.id, {
        notes: checkInNotes.trim() || null,
      });
      const detail = await fetchAppointment(appointment.id);
      setAppointment(detail.data);
      setCheckInOpen(false);
      setToastTitle("Customer checked in");
      setToastDescription("Status is CHECKED_IN. Complaint stays IN PROGRESS.");
      setToastOpen(true);
      onBooked?.();
      await load();
    } catch (err) {
      setCheckInError(
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Unable to check in.",
      );
    } finally {
      setCheckingIn(false);
    }
  }

  function openComplete() {
    setCompletionResult("COMPLETED");
    setCompletionNotes("");
    setCompleteError(null);
    setCompleteOpen(true);
  }

  function closeComplete() {
    if (completing) return;
    setCompleteOpen(false);
    setCompleteError(null);
  }

  async function confirmComplete() {
    if (!appointment) return;
    setCompleting(true);
    setCompleteError(null);
    try {
      await completeAppointment(appointment.id, {
        result: completionResult,
        notes: completionNotes.trim() || null,
      });
      const detail = await fetchAppointment(appointment.id);
      setAppointment(detail.data);
      setCompleteOpen(false);
      setToastTitle("Appointment completed");
      setToastDescription(
        "Status is COMPLETED. Complaint and escalation stay open.",
      );
      setToastOpen(true);
      onBooked?.();
      await load();
    } catch (err) {
      setCompleteError(
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Unable to complete appointment.",
      );
    } finally {
      setCompleting(false);
    }
  }

  function openNoShow() {
    setNoShowReason("");
    setNoShowError(null);
    setNoShowOpen(true);
  }

  function closeNoShow() {
    if (markingNoShow) return;
    setNoShowOpen(false);
    setNoShowError(null);
  }

  async function confirmNoShow() {
    if (!appointment) return;
    setMarkingNoShow(true);
    setNoShowError(null);
    try {
      await markAppointmentNoShow(appointment.id, {
        reason: noShowReason.trim() || null,
      });
      const detail = await fetchAppointment(appointment.id);
      setAppointment(detail.data);
      setNoShowOpen(false);
      setToastTitle("Customer marked as no-show");
      setToastDescription(
        "Status is NO_SHOW. Complaint and escalation stay open.",
      );
      setToastOpen(true);
      onBooked?.();
      await load();
    } catch (err) {
      setNoShowError(
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Unable to mark no-show.",
      );
    } finally {
      setMarkingNoShow(false);
    }
  }

  if (!loading && !escalation && !loadError) {
    return null;
  }

  const canCheckIn =
    canManage &&
    appointment?.status === "BOOKED" &&
    !appointment.checkedInAt &&
    !appointment.noShowAt;
  const canNoShow =
    canManage &&
    appointment?.status === "BOOKED" &&
    !appointment.noShowAt &&
    !appointment.checkedInAt;
  const canCompleteAction =
    canComplete &&
    appointment?.status === "CHECKED_IN" &&
    !appointment.completedAt;
  const isCompleted =
    appointment?.status === "COMPLETED" || Boolean(appointment?.completedAt);
  const isNoShow =
    appointment?.status === "NO_SHOW" || Boolean(appointment?.noShowAt);

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>Appointment</CardTitle>
        </CardHeader>
        <CardBody className="space-y-4">
          {loading ? (
            <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
              Loading appointment…
            </p>
          ) : loadError ? (
            <Alert
              tone="danger"
              title="Unable to load appointment"
              description={loadError}
              actionLabel="Retry"
              onAction={() => void load()}
            />
          ) : appointment ? (
            <div className="space-y-4">
              <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <DetailField label="Status" value={appointment.status} />
                <DetailField
                  label="Date"
                  value={formatDate(appointment.appointmentDate)}
                />
                <DetailField
                  label="Start"
                  value={formatTime(appointment.appointmentStartTime)}
                />
                <DetailField
                  label="End"
                  value={formatTime(appointment.appointmentEndTime)}
                />
                <DetailField
                  label="Engineer"
                  value={
                    appointment.assignedEngineerName?.trim() ||
                    appointment.assignedEngineerId
                  }
                />
                <DetailField
                  label="Notes"
                  value={appointment.notes?.trim() || "—"}
                />
              </dl>

              {appointment.status === "CHECKED_IN" ||
              appointment.status === "COMPLETED" ||
              appointment.checkedInAt ? (
                <div className="space-y-3 border-t border-ecmp-border pt-4">
                  <p className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-wide text-ecmp-text-secondary">
                    Check-In
                  </p>
                  <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <DetailField
                      label="Checked In At"
                      value={formatWhen(appointment.checkedInAt)}
                    />
                    <DetailField
                      label="Checked In By"
                      value={appointment.checkedInBy ?? "—"}
                    />
                    <DetailField
                      label="Check-In Notes"
                      value={appointment.checkinNotes?.trim() || "—"}
                    />
                  </dl>
                </div>
              ) : null}

              {isCompleted ? (
                <div className="space-y-3 border-t border-ecmp-border pt-4">
                  <p className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-wide text-ecmp-text-secondary">
                    Completion
                  </p>
                  <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <DetailField
                      label="Result"
                      value={appointment.completionResult?.trim() || "—"}
                    />
                    <DetailField
                      label="Completed At"
                      value={formatWhen(appointment.completedAt)}
                    />
                    <DetailField
                      label="Completed By"
                      value={appointment.completedBy ?? "—"}
                    />
                    <DetailField
                      label="Completion Notes"
                      value={appointment.completionNotes?.trim() || "—"}
                    />
                  </dl>
                </div>
              ) : null}

              {isNoShow ? (
                <div className="space-y-3 border-t border-ecmp-border pt-4">
                  <p className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-wide text-ecmp-text-secondary">
                    No Show
                  </p>
                  <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <DetailField
                      label="No Show At"
                      value={formatWhen(appointment.noShowAt)}
                    />
                    <DetailField
                      label="No Show By"
                      value={appointment.noShowBy ?? "—"}
                    />
                    <DetailField
                      label="Reason"
                      value={appointment.noShowReason?.trim() || "—"}
                    />
                  </dl>
                </div>
              ) : null}

              {canCheckIn || canNoShow ? (
                <div className="flex flex-wrap justify-end gap-2 border-t border-ecmp-border pt-4">
                  {canNoShow ? (
                    <Button
                      type="button"
                      variant="outline"
                      onClick={openNoShow}
                    >
                      Mark No Show
                    </Button>
                  ) : null}
                  {canCheckIn ? (
                    <Button
                      type="button"
                      variant="primary"
                      onClick={openCheckIn}
                    >
                      Check In
                    </Button>
                  ) : null}
                </div>
              ) : null}

              {canCompleteAction ? (
                <div className="flex flex-wrap justify-end gap-2 border-t border-ecmp-border pt-4">
                  <Button
                    type="button"
                    variant="primary"
                    onClick={openComplete}
                  >
                    Complete Appointment
                  </Button>
                </div>
              ) : null}

              {isCompleted ? (
                <div className="flex flex-wrap justify-end gap-2 border-t border-ecmp-border pt-4">
                  <Button type="button" variant="primary" disabled>
                    Complete Appointment
                  </Button>
                </div>
              ) : null}

              {isNoShow ? (
                <div className="flex flex-wrap justify-end gap-2 border-t border-ecmp-border pt-4">
                  <Button type="button" variant="outline" disabled>
                    Mark No Show
                  </Button>
                </div>
              ) : null}

              {appointment.status === "BOOKED" && !canManage ? (
                <p className="border-t border-ecmp-border pt-4 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
                  Awaiting Head Office Scheduler check-in.
                </p>
              ) : null}

              {appointment.status === "CHECKED_IN" && !canComplete ? (
                <p className="border-t border-ecmp-border pt-4 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
                  Awaiting Head Office Engineer completion.
                </p>
              ) : null}
            </div>
          ) : canManage ? (
            <form className="space-y-4" onSubmit={onSubmit}>
              <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
                Book a Head Office appointment for this approved escalation.
                Complaint stays IN PROGRESS.
              </p>
              {submitError ? (
                <Alert
                  tone="danger"
                  title="Booking failed"
                  description={submitError}
                />
              ) : null}
              {usersError ? (
                <Alert
                  tone="warning"
                  title="Engineer list unavailable"
                  description={usersError}
                />
              ) : null}
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <Input
                  label="Appointment Date"
                  name="appointmentDate"
                  type="date"
                  required
                  value={appointmentDate}
                  error={fieldErrors.appointmentDate}
                  onChange={(event) => setAppointmentDate(event.target.value)}
                />
                <Select
                  label="Assigned Engineer"
                  name="assignedEngineerId"
                  required
                  placeholder="Select engineer"
                  options={engineerOptions}
                  value={engineerId}
                  error={fieldErrors.assignedEngineerId}
                  onChange={(event) => setEngineerId(event.target.value)}
                />
                <Input
                  label="Start Time"
                  name="startTime"
                  type="time"
                  required
                  value={startTime}
                  error={fieldErrors.startTime}
                  onChange={(event) => setStartTime(event.target.value)}
                />
                <Input
                  label="End Time"
                  name="endTime"
                  type="time"
                  required
                  value={endTime}
                  error={fieldErrors.endTime}
                  onChange={(event) => setEndTime(event.target.value)}
                />
              </div>
              <Textarea
                label="Notes"
                name="notes"
                rows={2}
                value={notes}
                onChange={(event) => setNotes(event.target.value)}
              />
              <div className="flex flex-wrap justify-end gap-2">
                <Button type="submit" variant="primary" disabled={submitting}>
                  {submitting ? "Booking…" : "Book Appointment"}
                </Button>
              </div>
            </form>
          ) : (
            <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
              Awaiting Head Office Scheduler to book an appointment.
            </p>
          )}
        </CardBody>
      </Card>

      <Modal
        open={checkInOpen}
        onClose={closeCheckIn}
        title="Check in customer?"
        size="sm"
        footer={
          <>
            <Button
              type="button"
              variant="outline"
              disabled={checkingIn}
              onClick={closeCheckIn}
            >
              Cancel
            </Button>
            <Button
              type="button"
              variant="primary"
              disabled={checkingIn}
              onClick={() => void confirmCheckIn()}
            >
              {checkingIn ? "Checking in…" : "Confirm Check-In"}
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
            Confirm the customer has arrived. Appointment status becomes
            CHECKED_IN. Complaint stays IN PROGRESS.
          </p>
          {checkInError ? (
            <Alert
              tone="danger"
              title="Check-in failed"
              description={checkInError}
            />
          ) : null}
          <Textarea
            label="Check-In Notes"
            name="checkinNotes"
            rows={3}
            value={checkInNotes}
            onChange={(event) => setCheckInNotes(event.target.value)}
          />
        </div>
      </Modal>

      <Modal
        open={completeOpen}
        onClose={closeComplete}
        title="Complete appointment?"
        size="sm"
        footer={
          <>
            <Button
              type="button"
              variant="outline"
              disabled={completing}
              onClick={closeComplete}
            >
              Cancel
            </Button>
            <Button
              type="button"
              variant="primary"
              disabled={completing}
              onClick={() => void confirmComplete()}
            >
              {completing ? "Completing…" : "Confirm Completion"}
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
            Mark this meeting finished. Appointment status becomes COMPLETED.
            Complaint and escalation stay open.
          </p>
          {completeError ? (
            <Alert
              tone="danger"
              title="Completion failed"
              description={completeError}
            />
          ) : null}
          <Select
            label="Completion Result"
            name="completionResult"
            required
            options={COMPLETION_RESULT_OPTIONS}
            value={completionResult}
            onChange={(event) =>
              setCompletionResult(
                event.target.value as AppointmentCompletionResult,
              )
            }
          />
          <Textarea
            label="Completion Notes"
            name="completionNotes"
            rows={3}
            value={completionNotes}
            onChange={(event) => setCompletionNotes(event.target.value)}
          />
        </div>
      </Modal>

      <Modal
        open={noShowOpen}
        onClose={closeNoShow}
        title="Mark customer as no-show?"
        size="sm"
        footer={
          <>
            <Button
              type="button"
              variant="outline"
              disabled={markingNoShow}
              onClick={closeNoShow}
            >
              Cancel
            </Button>
            <Button
              type="button"
              variant="primary"
              disabled={markingNoShow}
              onClick={() => void confirmNoShow()}
            >
              {markingNoShow ? "Marking…" : "Confirm No Show"}
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
            Confirm the customer did not arrive. Appointment status becomes
            NO_SHOW. Complaint and escalation stay open.
          </p>
          {noShowError ? (
            <Alert
              tone="danger"
              title="No-show failed"
              description={noShowError}
            />
          ) : null}
          <Textarea
            label="Reason"
            name="noShowReason"
            rows={3}
            value={noShowReason}
            onChange={(event) => setNoShowReason(event.target.value)}
          />
        </div>
      </Modal>

      <Toast
        open={toastOpen}
        onClose={() => setToastOpen(false)}
        tone="success"
        title={toastTitle}
        description={toastDescription}
      />
    </>
  );
}
