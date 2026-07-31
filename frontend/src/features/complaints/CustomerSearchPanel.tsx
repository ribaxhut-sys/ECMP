"use client";

import { useCallback, useState, type FormEvent } from "react";
import {
  ApiError,
  confirmCmBatch1Customer,
  fetchCmBatch1Customer360,
  searchCmBatch1Customer,
  type CmBatch1Customer360Response,
  type CmBatch1CustomerCandidate,
  type CmBatch1VerificationStatus,
} from "@/lib/api";
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

const KEY_TYPE_OPTIONS = [
  { value: "customerNumber", label: "Customer number" },
  { value: "identityNumber", label: "Identity number" },
  { value: "referenceNumber", label: "Reference number" },
] as const;

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
        err instanceof ApiError
          ? err.message
          : "Unable to load Batch-1 Customer 360.",
      );
    } finally {
      setLoading360(false);
    }
  }

  async function onSearch(event: FormEvent): Promise<void> {
    event.preventDefault();
    const value = keyValue.trim();
    if (!value) {
      setError("Enter a search key.");
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
        setError("Customer search is blocked by enumeration protection.");
      } else if (data.verificationStatus === "not_found") {
        setError("No customer matched that key.");
      } else if (data.verificationStatus === "degraded") {
        setError(
          "Customer search is degraded. Confirm only if a candidate is still shown.",
        );
      }
    } catch (err) {
      resetSearchState();
      setError(
        err instanceof ApiError ? err.message : "Customer search failed.",
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
      setError("Select a customer candidate before confirming.");
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
        err instanceof ApiError
          ? err.message
          : "Unable to confirm customer.",
      );
    } finally {
      setConfirming(false);
    }
  }

  const locked = Boolean(confirmedCustomerId);

  return (
    <Card>
      <CardHeader>
        <CardTitle id="section-customer-search">Customer search</CardTitle>
        <CardDescription>
          SCR-CM-002 — search with exactly one key type, then confirm to lock
          CustomerId. Lab stub examples: CN-10001 / ID-10001 / REF-10001.
        </CardDescription>
      </CardHeader>
      <CardBody className="space-y-4">
        {error ? (
          <Alert tone="warning" title="Customer search" description={error} />
        ) : null}

        {locked ? (
          <Alert
            tone="success"
            title="Customer confirmed"
            description={`${confirmedDisplayName} (${confirmedCustomerId}) is locked for this create. Search again clears the lock.`}
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
            label="Key type"
            options={KEY_TYPE_OPTIONS}
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
            label="Key value"
            required
            value={keyValue}
            onChange={(event) => {
              setKeyValue(event.target.value);
              if (locked) clearConfirmation();
            }}
            disabled={disabled || searching}
            autoComplete="off"
            hint="Exactly one key type is sent to API-502"
          />
          <div className="flex items-end gap-2">
            <Button
              type="submit"
              loading={searching}
              disabled={disabled}
              aria-label="Search customer"
            >
              {searching ? "Searching…" : "Search"}
            </Button>
            {locked ? (
              <Button
                type="button"
                variant="outline"
                onClick={clearConfirmation}
                disabled={disabled}
              >
                Clear
              </Button>
            ) : null}
          </div>
        </form>

        {status ? (
          <p className="text-sm text-ecmp-text-secondary">
            Status: <span className="font-medium text-ecmp-text-primary">{status}</span>
            {enumerationOutcome ? ` · enumeration: ${enumerationOutcome}` : ""}
            {asOf ? ` · as of ${asOf}` : ""}
          </p>
        ) : null}

        {candidates.length > 0 ? (
          <fieldset className="space-y-2">
            <legend className="text-sm font-medium">Candidates</legend>
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
                {confirming ? "Confirming…" : "Confirm customer"}
              </Button>
            ) : null}
          </fieldset>
        ) : null}

        {locked && (loading360 || profile360) ? (
          <div className="rounded border border-ecmp-border p-3 text-sm">
            <h3 className="font-medium">Batch-1 Customer 360 (minimum)</h3>
            {loading360 ? (
              <p className="mt-2 text-ecmp-text-secondary">Loading profile…</p>
            ) : null}
            {profile360 ? (
              <dl className="mt-2 grid grid-cols-1 gap-2 md:grid-cols-2">
                <div>
                  <dt className="text-ecmp-text-secondary">Complaint count</dt>
                  <dd className="font-medium">{profile360.complaintCount}</dd>
                </div>
                <div>
                  <dt className="text-ecmp-text-secondary">Active complaints</dt>
                  <dd className="font-medium">
                    {profile360.activeComplaints?.length ?? 0}
                  </dd>
                </div>
                <div className="md:col-span-2">
                  <dt className="text-ecmp-text-secondary">asOf</dt>
                  <dd className="font-mono text-xs">{profile360.asOf}</dd>
                </div>
                <div className="md:col-span-2">
                  <dt className="text-ecmp-text-secondary">Profile (read-only)</dt>
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
