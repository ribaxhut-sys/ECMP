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
  fetchAppointment,
  fetchComplaintEscalations,
  fetchUsers,
  type UserRef,
} from "@/lib/api";
import type { Appointment, Escalation } from "@/lib/api/types";
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

  if (!loading && !escalation && !loadError) {
    return null;
  }

  const canCheckIn =
    canManage && appointment?.status === "BOOKED" && !appointment.checkedInAt;

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

              {canCheckIn ? (
                <div className="flex flex-wrap justify-end gap-2 border-t border-ecmp-border pt-4">
                  <Button type="button" variant="primary" onClick={openCheckIn}>
                    Check In
                  </Button>
                </div>
              ) : null}

              {appointment.status === "BOOKED" && !canManage ? (
                <p className="border-t border-ecmp-border pt-4 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
                  Awaiting Head Office Scheduler check-in.
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
