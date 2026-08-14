"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { useTranslations } from "next-intl";
import {
  confirmCmBatch1Customer,
  fetchCmBatch1Customer360,
  searchCmBatch1Customer,
  updateCustomerPhone,
  type CmBatch1ComplaintBrief,
  type CmBatch1Customer360Response,
  type CmBatch1CustomerCandidate,
  type CmBatch1VerificationStatus,
} from "@/lib/api";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import {
  Alert,
  Badge,
  Button,
  Card,
  CardBody,
  Empty,
  Input,
  Modal,
  SectionHeader,
  Skeleton,
} from "@/shared/ui";
import { formatDateTime24 } from "@/shared/utils/datetime";
import { validateCustomerSearchKey } from "./customerSearchKey";

export interface CustomerSearchPanelProps {
  confirmedCustomerId: string;
  confirmedDisplayName: string;
  onConfirmed: (payload: {
    customerId: string;
    displayName: string;
  }) => void;
  onCleared: () => void;
  /** Fired when Customer 360 loads or clears (active complaints for intake banner). */
  onActiveComplaintsChange?: (complaints: CmBatch1ComplaintBrief[]) => void;
  disabled?: boolean;
}

function profileText(
  profile: Record<string, unknown> | null | undefined,
  ...keys: string[]
): string | null {
  if (!profile) return null;
  for (const key of keys) {
    const value = profile[key];
    if (typeof value === "string" && value.trim()) return value.trim();
    if (typeof value === "number" && Number.isFinite(value)) return String(value);
  }
  return null;
}

function candidateExternalId(candidate: CmBatch1CustomerCandidate): string {
  const number = candidate.customerNumber?.trim();
  if (number) return number;
  // Prefer unmasked identity over legacy masked field.
  const masked = candidate.maskedIdentity?.trim();
  if (masked && !masked.includes("*")) return masked;
  return candidate.customerId;
}

/** Group digit-heavy IDs every 4 chars for scanability (display only). */
function formatCustomerIdDisplay(raw: string): string {
  const value = (raw || "").trim();
  if (!value) return value;
  const digits = value.replace(/\D+/g, "");
  // Only regroup when the value is essentially numeric ID/phone.
  if (digits.length >= 8 && digits.length === value.replace(/[\s-]/g, "").length) {
    return digits.replace(/(\d{4})(?=\d)/g, "$1 ").trim();
  }
  return value;
}

function candidatePhone(candidate: CmBatch1CustomerCandidate): string | null {
  const phone = candidate.phone?.trim();
  return phone || null;
}

function briefId(row: CmBatch1ComplaintBrief, index: number): string {
  return row.complaintId?.trim() || `complaint-${index}`;
}

type HistoryMode = "active" | "all";

/** 5 columns × 5 rows per page for ambiguous candidate picker. */
const CANDIDATE_PAGE_SIZE = 25;

function seedCandidateFromLock(
  customerId: string,
  displayName: string,
): CmBatch1CustomerCandidate {
  return {
    customerId,
    displayName: displayName.trim() || customerId,
  };
}

/**
 * SCR-CM-002 + SCR-CM-006 — Batch-1 customer search and 360 minimum.
 * Selection itself binds the customer (no separate confirm button).
 */
export function CustomerSearchPanel({
  confirmedCustomerId,
  confirmedDisplayName,
  onConfirmed,
  onCleared,
  onActiveComplaintsChange,
  disabled = false,
}: CustomerSearchPanelProps) {
  const t = useTranslations("complaints");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");
  const [keyValue, setKeyValue] = useState("");
  const [searching, setSearching] = useState(false);
  const [selecting, setSelecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<CmBatch1VerificationStatus | null>(null);
  const [candidates, setCandidates] = useState<CmBatch1CustomerCandidate[]>([]);
  const [candidatePage, setCandidatePage] = useState(1);
  /** After confirm, hide other matches until officer chooses "change selection". */
  const [showCandidatePicker, setShowCandidatePicker] = useState(true);
  const [selectedCandidateId, setSelectedCandidateId] = useState("");
  const [asOf, setAsOf] = useState<string | null>(null);
  const [enumerationOutcome, setEnumerationOutcome] = useState<string | null>(
    null,
  );
  const [profile360, setProfile360] =
    useState<CmBatch1Customer360Response | null>(null);
  const [loading360, setLoading360] = useState(false);
  const [phoneDraft, setPhoneDraft] = useState("");
  const [savingPhone, setSavingPhone] = useState(false);
  const [phoneInfo, setPhoneInfo] = useState<string | null>(null);
  const [historyMode, setHistoryMode] = useState<HistoryMode | null>(null);
  /** Last parent lock id applied into local locked UI (resume / prop sync). */
  const syncedLockIdRef = useRef("");

  const resetSearchState = useCallback(() => {
    setStatus(null);
    setCandidates([]);
    setCandidatePage(1);
    setShowCandidatePicker(true);
    setSelectedCandidateId("");
    setAsOf(null);
    setEnumerationOutcome(null);
    setProfile360(null);
    setPhoneDraft("");
    setPhoneInfo(null);
    setHistoryMode(null);
    setError(null);
  }, []);

  const clearConfirmation = useCallback(() => {
    syncedLockIdRef.current = "";
    resetSearchState();
    onCleared();
  }, [onCleared, resetSearchState]);

  const load360 = useCallback(
    async (customerId: string): Promise<void> => {
      setLoading360(true);
      setPhoneInfo(null);
      try {
        const res = await fetchCmBatch1Customer360(customerId);
        setProfile360(res.data);
        const profile = (res.data.profile ?? {}) as Record<string, unknown>;
        setPhoneDraft(
          profileText(profile, "phone", "phoneNumber", "referenceNumber") ??
            "",
        );
        const customerNumber = profileText(
          profile,
          "customerNumber",
          "customer_number",
          "externalId",
        );
        const nameFromProfile = profileText(
          profile,
          "displayName",
          "fullName",
          "name",
        );
        const phone = profileText(profile, "phone", "phoneNumber");
        if (customerNumber || nameFromProfile || phone) {
          setCandidates((prev) => {
            const idx = prev.findIndex((c) => c.customerId === customerId);
            if (idx < 0) {
              return [
                ...prev,
                {
                  customerId,
                  displayName: nameFromProfile || customerId,
                  customerNumber: customerNumber ?? null,
                  phone: phone ?? null,
                },
              ];
            }
            const current = prev[idx]!;
            const next: CmBatch1CustomerCandidate = {
              ...current,
              displayName:
                nameFromProfile || current.displayName || customerId,
              customerNumber:
                customerNumber ?? current.customerNumber ?? null,
              phone: phone ?? current.phone ?? null,
            };
            if (
              next.displayName === current.displayName &&
              next.customerNumber === current.customerNumber &&
              next.phone === current.phone
            ) {
              return prev;
            }
            const copy = prev.slice();
            copy[idx] = next;
            return copy;
          });
        }
      } catch (err) {
        setProfile360(null);
        setPhoneDraft("");
        setError(
          resolveApiErrorMessage(err, tErrors, tCommon, "unexpectedError") ||
            t("unableToLoadCustomer360"),
        );
      } finally {
        setLoading360(false);
      }
    },
    [t, tCommon, tErrors],
  );

  /**
   * Parent may restore customerId/name after Back from priority (draft resume)
   * while this panel remounts with empty local state — re-enter locked UI.
   */
  useEffect(() => {
    const id = confirmedCustomerId.trim();
    if (!id) {
      syncedLockIdRef.current = "";
      return;
    }
    if (syncedLockIdRef.current === id) return;
    syncedLockIdRef.current = id;

    setCandidates((prev) => {
      if (prev.some((c) => c.customerId === id)) return prev;
      return [seedCandidateFromLock(id, confirmedDisplayName)];
    });
    setSelectedCandidateId(id);
    setShowCandidatePicker(false);
    void load360(id);
  }, [confirmedCustomerId, confirmedDisplayName, load360]);

  useEffect(() => {
    onActiveComplaintsChange?.(profile360?.activeComplaints ?? []);
  }, [onActiveComplaintsChange, profile360]);

  async function onUpdatePhone(): Promise<void> {
    const customerId = confirmedCustomerId.trim();
    if (!customerId || savingPhone) return;
    setSavingPhone(true);
    setPhoneInfo(null);
    setError(null);
    try {
      const updated = await updateCustomerPhone(customerId, phoneDraft.trim());
      setPhoneDraft(updated.phone?.trim() || "");
      setPhoneInfo(t("phoneUpdated"));
      await load360(customerId);
    } catch (err) {
      setError(
        resolveApiErrorMessage(err, tErrors, tCommon, "unexpectedError") ||
          t("unableToUpdatePhone"),
      );
    } finally {
      setSavingPhone(false);
    }
  }

  async function selectCustomer(
    customerId: string,
    list: readonly CmBatch1CustomerCandidate[],
  ): Promise<void> {
    const id = customerId.trim();
    if (!id || selecting) return;

    setSelecting(true);
    setSelectedCandidateId(id);
    setError(null);
    try {
      await confirmCmBatch1Customer({ customerId: id });
      const match = list.find((row) => row.customerId === id);
      const displayName =
        match?.displayName?.trim() || confirmedDisplayName || id;
      syncedLockIdRef.current = id;
      onConfirmed({ customerId: id, displayName });
      setShowCandidatePicker(false);
      await load360(id);
    } catch (err) {
      setError(
        resolveApiErrorMessage(err, tErrors, tCommon, "unexpectedError") ||
          t("unableToConfirmCustomer"),
      );
    } finally {
      setSelecting(false);
    }
  }

  async function onSearch(
    event?: { preventDefault?: () => void },
  ): Promise<void> {
    event?.preventDefault?.();
    const value = keyValue.trim();
    const keyCheck = validateCustomerSearchKey(value);
    if (!keyCheck.ok) {
      const message =
        keyCheck.errorCode === "nameTooShort"
          ? t("searchNameTooShort")
          : keyCheck.errorCode === "idTooShort"
            ? t("searchIdTooShort")
            : keyCheck.errorCode === "phoneTooShort"
              ? t("searchPhoneTooShort")
              : t("enterSearchKey");
      setError(message);
      return;
    }

    setSearching(true);
    setError(null);
    setProfile360(null);
    if (confirmedCustomerId) {
      syncedLockIdRef.current = "";
      onCleared();
    }

    try {
      // Unified FR-002 search: name / ID / phone — always one key type (customerNumber).
      const res = await searchCmBatch1Customer({ customerNumber: value });
      const data = res.data;
      const list = data.candidates ?? [];
      setStatus(data.verificationStatus);
      setAsOf(data.asOf);
      setEnumerationOutcome(data.enumerationOutcome);
      setCandidates(list);
      setCandidatePage(1);
      setShowCandidatePicker(true);

      if (
        data.enumerationOutcome === "blocked" ||
        data.verificationStatus === "blocked"
      ) {
        setSelectedCandidateId("");
        setError(t("searchBlocked"));
        return;
      }
      if (data.verificationStatus === "not_found") {
        setSelectedCandidateId("");
        setError(t("noCustomerMatched"));
        return;
      }
      if (data.verificationStatus === "degraded") {
        setSelectedCandidateId("");
        setError(t("searchDegraded"));
        return;
      }

      // Exact match → bind immediately. Several names → show list for pick.
      if (data.verificationStatus === "verified" && data.customerId) {
        await selectCustomer(data.customerId, list);
      } else if (list.length === 1) {
        await selectCustomer(list[0]!.customerId, list);
      } else {
        setSelectedCandidateId("");
      }
    } catch (err) {
      resetSearchState();
      setError(
        resolveApiErrorMessage(err, tErrors, tCommon, "unexpectedError") ||
          t("searchFailed"),
      );
    } finally {
      setSearching(false);
    }
  }

  const locked = Boolean(confirmedCustomerId);
  const busy = searching || selecting;

  const candidateTotalPages = Math.max(
    1,
    Math.ceil(candidates.length / CANDIDATE_PAGE_SIZE),
  );
  const safeCandidatePage = Math.min(
    Math.max(1, candidatePage),
    candidateTotalPages,
  );
  const pagedCandidates = useMemo(() => {
    const start = (safeCandidatePage - 1) * CANDIDATE_PAGE_SIZE;
    return candidates.slice(start, start + CANDIDATE_PAGE_SIZE);
  }, [candidates, safeCandidatePage]);

  const selectedCandidate = useMemo(
    () =>
      candidates.find(
        (c) =>
          c.customerId === (selectedCandidateId || confirmedCustomerId),
      ) ?? null,
    [candidates, selectedCandidateId, confirmedCustomerId],
  );

  /** Full picker while choosing; after lock, only selected unless officer reopens. */
  const showFullCandidateList =
    candidates.length > 0 && (!locked || showCandidatePicker);
  /** Hide when Profil Wajib Pajak is showing — avoid duplicating name/ID/phone. */
  const showCollapsedSelection =
    locked &&
    !showCandidatePicker &&
    Boolean(selectedCandidate || confirmedCustomerId) &&
    !(loading360 || profile360);

  return (
    <section className="space-y-[var(--ecmp-panel-gap)]">
      <SectionHeader
        id="section-customer-search"
        title={t("customerSearchTitle")}
        description={t("customerSearchDescription")}
      />
      <Card>
        <CardBody className="space-y-[var(--ecmp-panel-gap)]">
        {error ? (
          <Alert
            tone="warning"
            title={t("customerSearchAlertTitle")}
            description={error}
          />
        ) : null}

        <div className="space-y-[var(--ecmp-form-gap)]">
          <div
            className="flex max-w-md flex-col gap-[var(--ecmp-form-gap)] sm:flex-row sm:items-end"
            aria-labelledby="section-customer-search"
          >
            <div className="min-w-0 flex-1">
              <Input
                name="keyValue"
                id="keyValue"
                label={t("customerSearchFieldLabel")}
                required
                value={keyValue}
                placeholder={t("customerSearchPlaceholder")}
                onChange={(event) => {
                  setKeyValue(event.target.value);
                  if (locked) clearConfirmation();
                }}
                onKeyDown={(event) => {
                  // Nested inside CreateComplaintView <form> — Enter must not
                  // submit the outer create form (was causing GET navigation).
                  if (event.key === "Enter") {
                    event.preventDefault();
                    void onSearch(event);
                  }
                }}
                disabled={disabled || busy}
                autoComplete="off"
                aria-describedby="keyValue-hint"
              />
            </div>
            <div className="flex shrink-0 gap-2">
              <Button
                type="button"
                loading={searching}
                disabled={disabled || selecting}
                aria-label={t("searchCustomerAria")}
                onClick={(event) => void onSearch(event)}
              >
                {searching ? t("searching") : tCommon("search")}
              </Button>
              {locked ? (
                <Button
                  type="button"
                  variant="outline"
                  onClick={clearConfirmation}
                  disabled={disabled || busy}
                >
                  {tCommon("clear")}
                </Button>
              ) : null}
            </div>
          </div>
          <p
            id="keyValue-hint"
            className="max-w-md text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary"
          >
            {t("keyValueHint")}
          </p>
        </div>

        {status ? (
          <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
            {t("statusLabel")}:{" "}
            <span className="font-medium text-ecmp-text-primary">
              {status === "verified"
                ? t("verificationVerified")
                : status === "not_found"
                  ? t("verificationNotFound")
                  : status === "ambiguous"
                    ? t("verificationAmbiguous")
                    : status === "degraded"
                      ? t("verificationDegraded")
                      : status === "blocked"
                        ? t("verificationBlocked")
                        : status}
            </span>
            {enumerationOutcome
              ? ` · ${
                  enumerationOutcome === "allowed"
                    ? t("matchAllowed")
                    : enumerationOutcome === "delayed"
                      ? t("matchDelayed")
                      : enumerationOutcome === "blocked"
                        ? t("matchBlocked")
                        : enumerationOutcome === "alerted"
                          ? t("matchAlerted")
                          : enumerationOutcome
                }`
              : ""}
            {asOf ? ` · ${t("asOfLabel")} ${asOf}` : ""}
          </p>
        ) : null}

        {showCollapsedSelection ? (
          <div className="flex flex-col gap-2 rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface p-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="min-w-0">
              <p className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                {t("selectedCandidateLabel")}
              </p>
              <p className="truncate text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                {selectedCandidate?.displayName?.trim() ||
                  confirmedDisplayName}
              </p>
              <p className="font-mono text-[length:var(--ecmp-font-body-small-size)] font-bold tabular-nums tracking-wide text-ecmp-text-primary">
                {selectedCandidate
                  ? formatCustomerIdDisplay(
                      candidateExternalId(selectedCandidate),
                    )
                  : formatCustomerIdDisplay(confirmedCustomerId)}
              </p>
              {selectedCandidate && candidatePhone(selectedCandidate) ? (
                <p className="truncate font-mono text-[length:var(--ecmp-font-helper-size)] tabular-nums text-ecmp-text-secondary">
                  {candidatePhone(selectedCandidate)}
                </p>
              ) : null}
              {candidates.length > 1 ? (
                <p className="mt-1 text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                  {t("otherCandidatesHidden", {
                    count: candidates.length - 1,
                  })}
                </p>
              ) : null}
            </div>
            {candidates.length > 1 ? (
              <Button
                type="button"
                variant="outline"
                size="sm"
                disabled={disabled || busy}
                onClick={() => {
                  setShowCandidatePicker(true);
                  if (confirmedCustomerId) {
                    const idx = candidates.findIndex(
                      (c) => c.customerId === confirmedCustomerId,
                    );
                    if (idx >= 0) {
                      setCandidatePage(
                        Math.floor(idx / CANDIDATE_PAGE_SIZE) + 1,
                      );
                    }
                  }
                }}
              >
                {t("changeCandidateSelection")}
              </Button>
            ) : null}
          </div>
        ) : null}

        {showFullCandidateList ? (
          <div className="space-y-3">
            <fieldset disabled={disabled || busy} className="min-w-0">
              <legend className="mb-2 text-[length:var(--ecmp-font-label-size)] font-[number:var(--ecmp-font-label-weight)] text-ecmp-text-primary">
                {candidates.length > 1
                  ? t("candidatesPickOne")
                  : t("candidates")}
              </legend>
              {/*
                Fixed 5×5 page: 5 columns × up to 5 rows (25 candidates).
                Narrow viewports step down so cards stay readable.
              */}
              <div
                className="grid grid-cols-1 gap-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5"
                role="radiogroup"
                aria-label={
                  candidates.length > 1
                    ? t("candidatesPickOne")
                    : t("candidates")
                }
              >
                {pagedCandidates.map((c) => {
                  const selected =
                    (selectedCandidateId || confirmedCustomerId) ===
                    c.customerId;
                  const inputId = `customer-candidate-${c.customerId}`;
                  return (
                    <label
                      key={c.customerId}
                      htmlFor={inputId}
                      className={
                        selected
                          ? "flex min-w-0 cursor-pointer items-start gap-2 rounded-[var(--ecmp-radius-md)] border border-ecmp-primary bg-ecmp-primary-muted/40 p-2.5"
                          : "flex min-w-0 cursor-pointer items-start gap-2 rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface p-2.5 hover:bg-ecmp-hover"
                      }
                    >
                      <input
                        id={inputId}
                        type="radio"
                        name="customerCandidate"
                        value={c.customerId}
                        checked={selected}
                        disabled={disabled || busy}
                        onChange={() => {
                          void selectCustomer(c.customerId, candidates);
                        }}
                        className="mt-1 shrink-0 accent-[var(--ecmp-color-primary)]"
                      />
                      <span className="min-w-0">
                        <span className="block break-all font-mono text-[length:var(--ecmp-font-body-small-size)] font-bold leading-snug tabular-nums tracking-wide text-ecmp-text-primary">
                          {formatCustomerIdDisplay(candidateExternalId(c))}
                        </span>
                        <span className="mt-0.5 block truncate text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                          {c.displayName}
                        </span>
                        {candidatePhone(c) ? (
                          <span className="mt-0.5 block truncate font-mono text-[length:var(--ecmp-font-helper-size)] tabular-nums text-ecmp-text-secondary">
                            {candidatePhone(c)}
                          </span>
                        ) : null}
                      </span>
                    </label>
                  );
                })}
              </div>
            </fieldset>
            {candidates.length > CANDIDATE_PAGE_SIZE ? (
              <div className="flex flex-wrap items-center justify-between gap-2">
                <p className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                  {t("candidatesPageSummary", {
                    shown: pagedCandidates.length,
                    total: candidates.length,
                    page: safeCandidatePage,
                    totalPages: candidateTotalPages,
                  })}
                </p>
                <div className="flex gap-2">
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    disabled={
                      disabled || busy || safeCandidatePage <= 1
                    }
                    onClick={() =>
                      setCandidatePage((p) => Math.max(1, p - 1))
                    }
                  >
                    {tCommon("previous")}
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    disabled={
                      disabled ||
                      busy ||
                      safeCandidatePage >= candidateTotalPages
                    }
                    onClick={() =>
                      setCandidatePage((p) =>
                        Math.min(candidateTotalPages, p + 1),
                      )
                    }
                  >
                    {tCommon("next")}
                  </Button>
                </div>
              </div>
            ) : null}
            {locked && candidates.length > 1 ? (
              <Button
                type="button"
                variant="outline"
                size="sm"
                disabled={disabled || busy}
                onClick={() => setShowCandidatePicker(false)}
              >
                {t("hideOtherCandidates")}
              </Button>
            ) : null}
          </div>
        ) : null}

        {locked && (loading360 || profile360) ? (
          <div className="space-y-[var(--ecmp-form-gap)] rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface-sunken p-3 text-[length:var(--ecmp-font-body-small-size)]">
            <h3 className="text-[length:var(--ecmp-font-card-title-size)] font-[number:var(--ecmp-font-card-title-weight)] text-ecmp-text-primary">
              {t("customer360Title")}
            </h3>
            {loading360 ? <Skeleton rows={3} /> : null}
            {profile360 ? (
              <div className="space-y-[var(--ecmp-form-gap)]">
                <dl className="grid grid-cols-1 gap-x-6 gap-y-2 sm:grid-cols-2">
                  {(() => {
                    const profile = (profile360.profile ?? {}) as Record<
                      string,
                      unknown
                    >;
                    const activeCount = profile360.activeComplaints?.length ?? 0;
                    const totalCount = profile360.complaintCount ?? 0;
                    return (
                      <>
                        <div className="space-y-1">
                          <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                            {t("profileName")}
                          </dt>
                          <dd className="font-medium text-ecmp-text-primary">
                            {profileText(
                              profile,
                              "displayName",
                              "fullName",
                              "name",
                            ) ?? confirmedDisplayName}
                          </dd>
                        </div>
                        <div className="space-y-1">
                          <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                            {t("activeComplaints")}
                          </dt>
                          <dd>
                            <button
                              type="button"
                              className="font-medium text-ecmp-primary underline underline-offset-2 hover:text-ecmp-primary/80 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ecmp-focus"
                              onClick={() => setHistoryMode("active")}
                              disabled={disabled}
                              aria-haspopup="dialog"
                              aria-label={t("activeComplaintsLinkAria", {
                                count: activeCount,
                              })}
                            >
                              {t("activeComplaintsLink", {
                                count: activeCount,
                              })}
                            </button>
                          </dd>
                        </div>
                        <div className="space-y-1">
                          <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                            {t("profileCustomerNumber")}
                          </dt>
                          <dd className="font-medium text-ecmp-text-primary">
                            {profileText(
                              profile,
                              "customerNumber",
                              "externalCustomerId",
                              "identityNumber",
                            ) ?? "—"}
                          </dd>
                        </div>
                        <div className="space-y-1">
                          <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                            {t("complaintCount")}
                          </dt>
                          <dd>
                            <button
                              type="button"
                              className="font-medium text-ecmp-primary underline underline-offset-2 hover:text-ecmp-primary/80 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ecmp-focus"
                              onClick={() => setHistoryMode("all")}
                              disabled={disabled}
                              aria-haspopup="dialog"
                              aria-label={t("complaintHistoryLinkAria", {
                                count: totalCount,
                              })}
                            >
                              {t("complaintHistoryLink", {
                                count: totalCount,
                              })}
                            </button>
                          </dd>
                        </div>
                      </>
                    );
                  })()}
                </dl>
                <div className="flex flex-col gap-2 sm:flex-row sm:items-end">
                  <div className="w-full max-w-[14rem]">
                    <Input
                      name="customerPhone"
                      id="customerPhone"
                      label={t("profilePhone")}
                      value={phoneDraft}
                      onChange={(event) => {
                        setPhoneDraft(event.target.value);
                        setPhoneInfo(null);
                      }}
                      disabled={disabled || savingPhone || loading360}
                      autoComplete="off"
                      inputMode="tel"
                      maxLength={32}
                    />
                  </div>
                  <Button
                    type="button"
                    variant="outline"
                    loading={savingPhone}
                    disabled={disabled || loading360}
                    onClick={() => void onUpdatePhone()}
                  >
                    {savingPhone ? t("updatingPhone") : t("updatePhone")}
                  </Button>
                </div>
                {phoneInfo ? (
                  <p className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                    {phoneInfo}
                  </p>
                ) : null}
              </div>
            ) : null}
          </div>
        ) : null}
        </CardBody>
      </Card>

      {profile360 && historyMode ? (
        <Modal
          open
          onClose={() => setHistoryMode(null)}
          title={
            historyMode === "active"
              ? t("customerHistoryActiveTitle")
              : t("customerHistoryTitle")
          }
          size="lg"
          footer={
            <Button
              type="button"
              variant="outline"
              onClick={() => setHistoryMode(null)}
            >
              {tCommon("closeDialog")}
            </Button>
          }
        >
          <CustomerComplaintHistoryList
            rows={
              historyMode === "active"
                ? (profile360.activeComplaints ?? [])
                : (profile360.complaintHistory ??
                  profile360.activeComplaints ??
                  [])
            }
            emptyLabel={t("customerHistoryEmpty")}
            hint={t("customerHistoryHint")}
            openLabel={t("openComplaintInNewTab")}
            statusOpenLabel={t("statusOpen")}
            statusClosedLabel={t("statusClosed")}
          />
        </Modal>
      ) : null}
    </section>
  );
}

function CustomerComplaintHistoryList({
  rows,
  emptyLabel,
  hint,
  openLabel,
  statusOpenLabel,
  statusClosedLabel,
}: {
  rows: CmBatch1ComplaintBrief[];
  emptyLabel: string;
  hint: string;
  openLabel: string;
  statusOpenLabel: string;
  statusClosedLabel: string;
}) {
  if (rows.length === 0) {
    return <Empty title={emptyLabel} description={hint} />;
  }
  return (
    <div className="space-y-[var(--ecmp-panel-gap)]">
      <p className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
        {hint}
      </p>
      <ul className="max-h-80 space-y-2 overflow-auto">
        {rows.map((row, index) => {
          const id = briefId(row, index);
          const number = row.complaintNumber?.trim() || id;
          const isClosed = (row.status || "").toUpperCase() === "CLOSED";
          const created = formatDateTime24(row.createdAt);
          const href = `/complaints/cm/${encodeURIComponent(id)}`;
          return (
            <li
              key={id}
              className="rounded-[var(--ecmp-radius-md)] border border-ecmp-border p-3"
            >
              <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                <div className="min-w-0 space-y-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="font-mono text-[length:var(--ecmp-font-body-small-size)] font-medium">
                      {number}
                    </span>
                    <Badge tone={isClosed ? "success" : "info"}>
                      {isClosed ? statusClosedLabel : statusOpenLabel}
                    </Badge>
                  </div>
                  {row.subject?.trim() ? (
                    <p className="text-ecmp-text-primary">{row.subject}</p>
                  ) : null}
                  {created ? (
                    <p className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                      {created}
                    </p>
                  ) : null}
                </div>
                {row.complaintId ? (
                  <Link
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex shrink-0 items-center justify-center rounded-[var(--ecmp-radius-button)] border border-ecmp-border bg-ecmp-surface px-3 py-1.5 text-[length:var(--ecmp-font-helper-size)] font-medium text-ecmp-primary underline-offset-2 hover:bg-ecmp-hover hover:underline"
                  >
                    {openLabel}
                  </Link>
                ) : null}
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
