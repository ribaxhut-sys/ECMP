"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type FormEvent,
} from "react";
import { useLocale, useTranslations } from "next-intl";
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
import { formatDate, formatDateTime } from "@/i18n/formatting";
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

function formatTime(value: string | null | undefined, emDash: string): string {
  if (!value) return emDash;
  return value.length >= 5 ? value.slice(0, 5) : value;
}

function DetailField({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-0 space-y-1">
      <dt className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
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
  const t = useTranslations("complaints");
  const tCommon = useTranslations("common");
  const locale = useLocale();
  const canManage = hasPermission("escalations:review");
  const canComplete = hasPermission("appointments:complete");

  const COMPLETION_RESULT_OPTIONS = [
    { value: "COMPLETED", label: t("completed") },
    { value: "PARTIALLY_COMPLETED", label: t("partiallyCompleted") },
  ];

  function roleLabel(user: UserRef): string {
    return user.roleName?.trim() || user.roleCode?.trim() || tCommon("emDash");
  }

  function userOptionLabel(user: UserRef): string {
    return `${user.fullName} — ${roleLabel(user)}`;
  }

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
  const [toastTitle, setToastTitle] = useState("");
  const [toastDescription, setToastDescription] = useState("");

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
            err instanceof ApiError ? err.message : t("unableToLoadUsers"),
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
            : t("unableToLoadAppointment"),
      );
      setEscalation(null);
      setAppointment(null);
    } finally {
      setLoading(false);
    }
  }, [canManage, complaintId, t]);

  useEffect(() => {
    void load();
  }, [load, refreshKey]);

  const engineerOptions = useMemo(
    () =>
      users.map((user) => ({
        value: user.id,
        label: userOptionLabel(user),
      })),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [users],
  );

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (!escalation) return;

    const errors: Record<string, string> = {};
    if (!appointmentDate.trim()) errors.appointmentDate = t("dateRequired");
    if (!startTime.trim()) errors.startTime = t("startTimeRequired");
    if (!endTime.trim()) errors.endTime = t("endTimeRequired");
    if (!engineerId) errors.assignedEngineerId = t("engineerRequired");
    if (startTime && endTime && endTime <= startTime) {
      errors.endTime = t("endTimeAfterStart");
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
      setToastTitle(t("appointmentBooked"));
      setToastDescription(t("timelineUpdatedEscalationApproved"));
      setToastOpen(true);
      onBooked?.();
      await load();
    } catch (err) {
      setSubmitError(
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : t("unableToBookAppointment"),
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
      setToastTitle(t("customerCheckedIn"));
      setToastDescription(t("statusCheckedInHint"));
      setToastOpen(true);
      onBooked?.();
      await load();
    } catch (err) {
      setCheckInError(
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : t("unableToCheckIn"),
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
      setToastTitle(t("appointmentCompleted"));
      setToastDescription(t("statusCompletedHint"));
      setToastOpen(true);
      onBooked?.();
      await load();
    } catch (err) {
      setCompleteError(
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : t("unableToCompleteAppointment"),
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
      setToastTitle(t("customerMarkedNoShow"));
      setToastDescription(t("statusNoShowHint"));
      setToastOpen(true);
      onBooked?.();
      await load();
    } catch (err) {
      setNoShowError(
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : t("unableToMarkNoShow"),
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
          <CardTitle>{t("appointmentCard")}</CardTitle>
        </CardHeader>
        <CardBody className="space-y-[var(--ecmp-panel-gap)]">
          {loading ? (
            <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
              {t("loadingAppointment")}
            </p>
          ) : loadError ? (
            <Alert
              tone="danger"
              title={t("unableToLoadAppointment")}
              description={loadError}
              actionLabel={tCommon("retry")}
              onAction={() => void load()}
            />
          ) : appointment ? (
            <div className="space-y-[var(--ecmp-panel-gap)]">
              <dl className="grid grid-cols-1 gap-[var(--ecmp-form-gap)] sm:grid-cols-2">
                <DetailField label={t("status")} value={appointment.status} />
                <DetailField
                  label={t("appointmentDate")}
                  value={formatDate(appointment.appointmentDate, locale)}
                />
                <DetailField
                  label={t("startTime")}
                  value={formatTime(appointment.appointmentStartTime, tCommon("emDash"))}
                />
                <DetailField
                  label={t("endTime")}
                  value={formatTime(appointment.appointmentEndTime, tCommon("emDash"))}
                />
                <DetailField
                  label={t("engineer")}
                  value={
                    appointment.assignedEngineerName?.trim() ||
                    appointment.assignedEngineerId
                  }
                />
                <DetailField
                  label={t("notes")}
                  value={appointment.notes?.trim() || tCommon("emDash")}
                />
              </dl>

              {appointment.status === "CHECKED_IN" ||
              appointment.status === "COMPLETED" ||
              appointment.checkedInAt ? (
                <div className="space-y-3 border-t border-ecmp-border pt-[var(--ecmp-panel-gap)]">
                  <p className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                    {t("checkIn")}
                  </p>
                  <dl className="grid grid-cols-1 gap-[var(--ecmp-form-gap)] sm:grid-cols-2">
                    <DetailField
                      label={t("checkedInAt")}
                      value={formatDateTime(appointment.checkedInAt, locale)}
                    />
                    <DetailField
                      label={t("checkedInBy")}
                      value={appointment.checkedInBy ?? tCommon("emDash")}
                    />
                    <DetailField
                      label={t("checkInNotes")}
                      value={appointment.checkinNotes?.trim() || tCommon("emDash")}
                    />
                  </dl>
                </div>
              ) : null}

              {isCompleted ? (
                <div className="space-y-3 border-t border-ecmp-border pt-[var(--ecmp-panel-gap)]">
                  <p className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                    {t("completion")}
                  </p>
                  <dl className="grid grid-cols-1 gap-[var(--ecmp-form-gap)] sm:grid-cols-2">
                    <DetailField
                      label={t("result")}
                      value={appointment.completionResult?.trim() || tCommon("emDash")}
                    />
                    <DetailField
                      label={t("completedAt")}
                      value={formatDateTime(appointment.completedAt, locale)}
                    />
                    <DetailField
                      label={t("completedBy")}
                      value={appointment.completedBy ?? tCommon("emDash")}
                    />
                    <DetailField
                      label={t("completionNotes")}
                      value={appointment.completionNotes?.trim() || tCommon("emDash")}
                    />
                  </dl>
                </div>
              ) : null}

              {isNoShow ? (
                <div className="space-y-3 border-t border-ecmp-border pt-[var(--ecmp-panel-gap)]">
                  <p className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                    {t("noShow")}
                  </p>
                  <dl className="grid grid-cols-1 gap-[var(--ecmp-form-gap)] sm:grid-cols-2">
                    <DetailField
                      label={t("noShowAt")}
                      value={formatDateTime(appointment.noShowAt, locale)}
                    />
                    <DetailField
                      label={t("noShowBy")}
                      value={appointment.noShowBy ?? tCommon("emDash")}
                    />
                    <DetailField
                      label={t("reason")}
                      value={appointment.noShowReason?.trim() || tCommon("emDash")}
                    />
                  </dl>
                </div>
              ) : null}

              {canCheckIn || canNoShow ? (
                <div className="flex flex-wrap justify-end gap-2 border-t border-ecmp-border pt-[var(--ecmp-panel-gap)]">
                  {canNoShow ? (
                    <Button
                      type="button"
                      variant="outline"
                      onClick={openNoShow}
                    >
                      {t("markNoShow")}
                    </Button>
                  ) : null}
                  {canCheckIn ? (
                    <Button
                      type="button"
                      variant="primary"
                      onClick={openCheckIn}
                    >
                      {t("checkIn")}
                    </Button>
                  ) : null}
                </div>
              ) : null}

              {canCompleteAction ? (
                <div className="flex flex-wrap justify-end gap-2 border-t border-ecmp-border pt-[var(--ecmp-panel-gap)]">
                  <Button
                    type="button"
                    variant="primary"
                    onClick={openComplete}
                  >
                    {t("completeAppointment")}
                  </Button>
                </div>
              ) : null}

              {isCompleted ? (
                <div className="flex flex-wrap justify-end gap-2 border-t border-ecmp-border pt-[var(--ecmp-panel-gap)]">
                  <Button type="button" variant="primary" disabled>
                    {t("completeAppointment")}
                  </Button>
                </div>
              ) : null}

              {isNoShow ? (
                <div className="flex flex-wrap justify-end gap-2 border-t border-ecmp-border pt-[var(--ecmp-panel-gap)]">
                  <Button type="button" variant="outline" disabled>
                    {t("markNoShow")}
                  </Button>
                </div>
              ) : null}

              {appointment.status === "BOOKED" && !canManage ? (
                <p className="border-t border-ecmp-border pt-[var(--ecmp-panel-gap)] text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
                  {t("awaitingHeadOfficeSchedulerCheckIn")}
                </p>
              ) : null}

              {appointment.status === "CHECKED_IN" && !canComplete ? (
                <p className="border-t border-ecmp-border pt-[var(--ecmp-panel-gap)] text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
                  {t("awaitingHeadOfficeEngineerCompletion")}
                </p>
              ) : null}
            </div>
          ) : canManage ? (
            <form className="space-y-[var(--ecmp-panel-gap)]" onSubmit={onSubmit}>
              <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
                {t("bookAppointmentHint")}
              </p>
              {submitError ? (
                <Alert
                  tone="danger"
                  title={t("bookingFailed")}
                  description={submitError}
                />
              ) : null}
              {usersError ? (
                <Alert
                  tone="warning"
                  title={t("engineerListUnavailable")}
                  description={usersError}
                />
              ) : null}
              <div className="grid grid-cols-1 gap-[var(--ecmp-form-gap)] md:grid-cols-2">
                <Input
                  label={t("appointmentDate")}
                  name="appointmentDate"
                  type="date"
                  required
                  value={appointmentDate}
                  error={fieldErrors.appointmentDate}
                  onChange={(event) => setAppointmentDate(event.target.value)}
                />
                <Select
                  label={t("assignedEngineer")}
                  name="assignedEngineerId"
                  required
                  placeholder={t("selectEngineer")}
                  options={engineerOptions}
                  value={engineerId}
                  error={fieldErrors.assignedEngineerId}
                  onChange={(event) => setEngineerId(event.target.value)}
                />
                <Input
                  label={t("startTime")}
                  name="startTime"
                  type="time"
                  required
                  value={startTime}
                  error={fieldErrors.startTime}
                  onChange={(event) => setStartTime(event.target.value)}
                />
                <Input
                  label={t("endTime")}
                  name="endTime"
                  type="time"
                  required
                  value={endTime}
                  error={fieldErrors.endTime}
                  onChange={(event) => setEndTime(event.target.value)}
                />
              </div>
              <Textarea
                label={t("notes")}
                name="notes"
                rows={2}
                value={notes}
                onChange={(event) => setNotes(event.target.value)}
              />
              <div className="flex flex-wrap justify-end gap-2">
                <Button type="submit" variant="primary" disabled={submitting}>
                  {submitting ? t("booking") : t("bookAppointment")}
                </Button>
              </div>
            </form>
          ) : (
            <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
              {t("awaitingHeadOfficeSchedulerBook")}
            </p>
          )}
        </CardBody>
      </Card>

      <Modal
        open={checkInOpen}
        onClose={closeCheckIn}
        title={t("checkInCustomerConfirm")}
        size="sm"
        footer={
          <>
            <Button
              type="button"
              variant="outline"
              disabled={checkingIn}
              onClick={closeCheckIn}
            >
              {tCommon("cancel")}
            </Button>
            <Button
              type="button"
              variant="primary"
              disabled={checkingIn}
              onClick={() => void confirmCheckIn()}
            >
              {checkingIn ? t("checkingIn") : t("confirmCheckIn")}
            </Button>
          </>
        }
      >
        <div className="space-y-[var(--ecmp-panel-gap)]">
          <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
            {t("confirmCheckInHint")}
          </p>
          {checkInError ? (
            <Alert
              tone="danger"
              title={t("checkInFailed")}
              description={checkInError}
            />
          ) : null}
          <Textarea
            label={t("checkInNotes")}
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
        title={t("completeAppointmentConfirm")}
        size="sm"
        footer={
          <>
            <Button
              type="button"
              variant="outline"
              disabled={completing}
              onClick={closeComplete}
            >
              {tCommon("cancel")}
            </Button>
            <Button
              type="button"
              variant="primary"
              disabled={completing}
              onClick={() => void confirmComplete()}
            >
              {completing ? t("completing") : t("confirmCompletion")}
            </Button>
          </>
        }
      >
        <div className="space-y-[var(--ecmp-panel-gap)]">
          <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
            {t("confirmCompletionHint")}
          </p>
          {completeError ? (
            <Alert
              tone="danger"
              title={t("completionFailed")}
              description={completeError}
            />
          ) : null}
          <Select
            label={t("completionResult")}
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
            label={t("completionNotes")}
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
        title={t("markNoShowConfirm")}
        size="sm"
        footer={
          <>
            <Button
              type="button"
              variant="outline"
              disabled={markingNoShow}
              onClick={closeNoShow}
            >
              {tCommon("cancel")}
            </Button>
            <Button
              type="button"
              variant="primary"
              disabled={markingNoShow}
              onClick={() => void confirmNoShow()}
            >
              {markingNoShow ? t("marking") : t("confirmNoShow")}
            </Button>
          </>
        }
      >
        <div className="space-y-[var(--ecmp-panel-gap)]">
          <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
            {t("confirmNoShowHint")}
          </p>
          {noShowError ? (
            <Alert
              tone="danger"
              title={t("noShowFailed")}
              description={noShowError}
            />
          ) : null}
          <Textarea
            label={t("reason")}
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
