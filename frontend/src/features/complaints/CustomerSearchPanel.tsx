"use client";

import { useCallback, useMemo, useState, type FormEvent } from "react";
import { useTranslations } from "next-intl";
import {
  ApiError,
  confirmCmBatch1Customer,
  fetchCmBatch1Customer360,
  searchCmBatch1Customer,
  type CmBatch1Customer360Response,
  type CmBatch1CustomerCandidate,
  type CmBatch1VerificationStatus,
} from "@/lib/api";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import {
  Alert,
  Button,
  Card,
  CardBody,
  CardDescription,
  CardHeader,
  CardTitle,
  Input,
  Select,
} from "@/shared/ui";

export type CustomerKeyType =
  | "customerNumber"
  | "identityNumber"
  | "referenceNumber";

export interface CustomerSearchPanelProps {
  confirmedCustomerId: string;
  confirmedDisplayName: string;
  onConfirmed: (payload: {
    customerId: string;
    displayName: string;
  }) => void;
  onCleared: () => void;
  disabled?: boolean;
}

/**
 * SCR-CM-002 + SCR-CM-006 — Batch-1 customer search, confirm, and 360 minimum.
 */
export function CustomerSearchPanel({
  confirmedCustomerId,
  confirmedDisplayName,
  onConfirmed,
  onCleared,
  disabled = false,
}: CustomerSearchPanelProps) {
  const t = useTranslations("complaints");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");
  const [keyType, setKeyType] = useState<CustomerKeyType>("customerNumber");
  const [keyValue, setKeyValue] = useState("");
  const [searching, setSearching] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<CmBatch1VerificationStatus | null>(null);
  const [candidates, setCandidates] = useState<CmBatch1CustomerCandidate[]>([]);
  const [selectedCandidateId, setSelectedCandidateId] = useState("");
  const [asOf, setAsOf] = useState<string | null>(null);
  const [enumerationOutcome, setEnumerationOutcome] = useState<string | null>(
    null,
  );
  const [profile360, setProfile360] =
    useState<CmBatch1Customer360Response | null>(null);
  const [loading360, setLoading360] = useState(false);

  const keyTypeOptions = useMemo(
    () => [
      { value: "customerNumber", label: t("customerNumber") },
      { value: "identityNumber", label: t("identityNumber") },
      { value: "referenceNumber", label: t("referenceNumber") },
    ],
    [t],
  );

  const resetSearchState = useCallback(() => {
    setStatus(null);
    setCandidates([]);
    setSelectedCandidateId("");
    setAsOf(null);
    setEnumerationOutcome(null);
    setProfile360(null);
    setError(null);
  }, []);

  const clearConfirmation = useCallback(() => {
    resetSearchState();
    onCleared();
  }, [onCleared, resetSearchState]);

  async function load360(customerId: string): Promise<void> {
    setLoading360(true);
    try {
      const res = await fetchCmBatch1Customer360(customerId);
      setProfile360(res.data);
    } catch (err) {
      setProfile360(null);
      setError(
        resolveApiErrorMessage(err, tErrors, tCommon, "unexpectedError") ||
          t("unableToLoadCustomer360"),
      );
    } finally {
      setLoading360(false);
    }
  }

  async function onSearch(event: FormEvent): Promise<void> {
    event.preventDefault();
    const value = keyValue.trim();
    if (!value) {
      setError(t("enterSearchKey"));
      return;
    }

    setSearching(true);
    setError(null);
    setProfile360(null);
    if (confirmedCustomerId) {
      onCleared();
    }

    try {
      const body =
        keyType === "customerNumber"
          ? { customerNumber: value }
          : keyType === "identityNumber"
            ? { identityNumber: value }
            : { referenceNumber: value };

      const res = await searchCmBatch1Customer(body);
      const data = res.data;
      setStatus(data.verificationStatus);
      setAsOf(data.asOf);
      setEnumerationOutcome(data.enumerationOutcome);
      setCandidates(data.candidates ?? []);

      if (data.verificationStatus === "verified" && data.customerId) {
        setSelectedCandidateId(data.customerId);
      } else if ((data.candidates ?? []).length === 1) {
        setSelectedCandidateId(data.candidates[0].customerId);
      } else {
        setSelectedCandidateId("");
      }

      if (
        data.enumerationOutcome === "blocked" ||
        data.verificationStatus === "blocked"
      ) {
        setError(t("searchBlocked"));
      } else if (data.verificationStatus === "not_found") {
        setError(t("noCustomerMatched"));
      } else if (data.verificationStatus === "degraded") {
        setError(t("searchDegraded"));
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

  async function onConfirm(): Promise<void> {
    const customerId =
      selectedCandidateId.trim() ||
      candidates.find((c) => c.customerId)?.customerId ||
      "";
    if (!customerId) {
      setError(t("selectCandidateBeforeConfirm"));
      return;
    }

    setConfirming(true);
    setError(null);
    try {
      await confirmCmBatch1Customer({ customerId });
      const match = candidates.find((c) => c.customerId === customerId);
      const displayName =
        match?.displayName?.trim() ||
        confirmedDisplayName ||
        customerId;
      onConfirmed({ customerId, displayName });
      await load360(customerId);
    } catch (err) {
      setError(
        resolveApiErrorMessage(err, tErrors, tCommon, "unexpectedError") ||
          t("unableToConfirmCustomer"),
      );
    } finally {
      setConfirming(false);
    }
  }

  const locked = Boolean(confirmedCustomerId);

  return (
    <Card>
      <CardHeader>
        <CardTitle id="section-customer-search">
          {t("customerSearchTitle")}
        </CardTitle>
        <CardDescription>{t("customerSearchDescription")}</CardDescription>
      </CardHeader>
      <CardBody className="space-y-4">
        {error ? (
          <Alert
            tone="warning"
            title={t("customerSearchAlertTitle")}
            description={error}
          />
        ) : null}

        {locked ? (
          <Alert
            tone="success"
            title={t("customerConfirmed")}
            description={t("customerConfirmedDescription", {
              name: confirmedDisplayName,
              id: confirmedCustomerId,
            })}
          />
        ) : null}

        <form
          onSubmit={(event) => void onSearch(event)}
          className="grid grid-cols-1 gap-4 md:grid-cols-3"
          aria-labelledby="section-customer-search"
        >
          <Select
            name="keyType"
            id="keyType"
            label={t("keyType")}
            options={keyTypeOptions}
            value={keyType}
            onChange={(event) => {
              setKeyType(event.target.value as CustomerKeyType);
              clearConfirmation();
            }}
            disabled={disabled || searching}
          />
          <Input
            name="keyValue"
            id="keyValue"
            label={t("keyValue")}
            required
            value={keyValue}
            onChange={(event) => {
              setKeyValue(event.target.value);
              if (locked) clearConfirmation();
            }}
            disabled={disabled || searching}
            autoComplete="off"
            hint={t("keyValueHint")}
          />
          <div className="flex items-end gap-2">
            <Button
              type="submit"
              loading={searching}
              disabled={disabled}
              aria-label={t("searchCustomerAria")}
            >
              {searching ? t("searching") : tCommon("search")}
            </Button>
            {locked ? (
              <Button
                type="button"
                variant="outline"
                onClick={clearConfirmation}
                disabled={disabled}
              >
                {tCommon("clear")}
              </Button>
            ) : null}
          </div>
        </form>

        {status ? (
          <p className="text-sm text-ecmp-text-secondary">
            {t("statusLabel")}:{" "}
            <span className="font-medium text-ecmp-text-primary">{status}</span>
            {enumerationOutcome
              ? ` · ${t("enumerationLabel")}: ${enumerationOutcome}`
              : ""}
            {asOf ? ` · ${t("asOfLabel")} ${asOf}` : ""}
          </p>
        ) : null}

        {candidates.length > 0 ? (
          <fieldset className="space-y-2">
            <legend className="text-sm font-medium">{t("candidates")}</legend>
            <ul className="space-y-2">
              {candidates.map((c) => (
                <li key={c.customerId}>
                  <label className="flex cursor-pointer items-start gap-2 rounded border border-ecmp-border p-3 text-sm">
                    <input
                      type="radio"
                      name="customerCandidate"
                      value={c.customerId}
                      checked={selectedCandidateId === c.customerId}
                      onChange={() => setSelectedCandidateId(c.customerId)}
                      disabled={disabled || confirming}
                      className="mt-1"
                    />
                    <span>
                      <span className="font-medium">{c.displayName}</span>
                      <span className="block font-mono text-xs text-ecmp-text-secondary">
                        {c.customerId}
                        {c.maskedIdentity ? ` · ${c.maskedIdentity}` : ""}
                      </span>
                    </span>
                  </label>
                </li>
              ))}
            </ul>
            {!locked ? (
              <Button
                type="button"
                onClick={() => void onConfirm()}
                loading={confirming}
                disabled={disabled || !selectedCandidateId}
              >
                {confirming ? t("confirming") : t("confirmCustomer")}
              </Button>
            ) : null}
          </fieldset>
        ) : null}

        {locked && (loading360 || profile360) ? (
          <div className="rounded border border-ecmp-border p-3 text-sm">
            <h3 className="font-medium">{t("customer360Title")}</h3>
            {loading360 ? (
              <p className="mt-2 text-ecmp-text-secondary">
                {t("loadingProfile")}
              </p>
            ) : null}
            {profile360 ? (
              <dl className="mt-2 grid grid-cols-1 gap-2 md:grid-cols-2">
                <div>
                  <dt className="text-ecmp-text-secondary">
                    {t("complaintCount")}
                  </dt>
                  <dd className="font-medium">{profile360.complaintCount}</dd>
                </div>
                <div>
                  <dt className="text-ecmp-text-secondary">
                    {t("activeComplaints")}
                  </dt>
                  <dd className="font-medium">
                    {profile360.activeComplaints?.length ?? 0}
                  </dd>
                </div>
                <div className="md:col-span-2">
                  <dt className="text-ecmp-text-secondary">{t("asOfLabel")}</dt>
                  <dd className="font-mono text-xs">{profile360.asOf}</dd>
                </div>
                <div className="md:col-span-2">
                  <dt className="text-ecmp-text-secondary">
                    {t("profileReadOnly")}
                  </dt>
                  <dd>
                    <pre className="mt-1 max-h-40 overflow-auto rounded bg-ecmp-secondary-muted p-2 text-xs">
                      {JSON.stringify(profile360.profile ?? {}, null, 2)}
                    </pre>
                  </dd>
                </div>
              </dl>
            ) : null}
          </div>
        ) : null}
      </CardBody>
    </Card>
  );
}
