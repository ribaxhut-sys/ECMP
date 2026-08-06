"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import {
  Alert,
  Button,
  Card,
  CardBody,
  CardHeader,
  Input,
} from "@/shared/ui";
import type { MockCustomer } from "@/features/supervisor-assign/mock/assignmentRepository";
import { searchCustomers } from "@/features/supervisor-assign/mock/assignmentRepository";

export interface CustomerReferencePanelProps {
  selected: MockCustomer | null;
  onSelect: (customer: MockCustomer) => void;
  onClear: () => void;
}

/**
 * Customer reference lookup — cache/reference only.
 * ECMP is not Customer Master SoR (SCR-WS-01).
 */
export function CustomerReferencePanel({
  selected,
  onSelect,
  onClear,
}: CustomerReferencePanelProps) {
  const t = useTranslations("intake");
  const [query, setQuery] = useState("");
  const [hits, setHits] = useState<MockCustomer[]>([]);

  function runSearch(): void {
    setHits(searchCustomers(query));
  }

  return (
    <Card>
      <CardHeader>
        <h2 className="text-[length:var(--ecmp-font-card-title-size)] font-semibold text-ecmp-text-primary">
          {t("customerTitle")}
        </h2>
        <p className="mt-1 text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
          {t("customerHint")}
        </p>
      </CardHeader>
      <CardBody className="space-y-4">
        {selected ? (
          <div className="space-y-3 rounded-[var(--ecmp-radius-md)] border border-ecmp-border/70 bg-ecmp-surface-sunken/40 p-3">
            <dl className="grid gap-2 sm:grid-cols-2">
              <div>
                <dt className="text-[length:var(--ecmp-font-overline-size)] uppercase tracking-wide text-ecmp-text-secondary">
                  {t("fieldCustomerRef")}
                </dt>
                <dd className="text-ecmp-text-primary">{selected.ref}</dd>
              </div>
              <div>
                <dt className="text-[length:var(--ecmp-font-overline-size)] uppercase tracking-wide text-ecmp-text-secondary">
                  {t("fieldCustomerName")}
                </dt>
                <dd className="text-ecmp-text-primary">{selected.name}</dd>
              </div>
              <div>
                <dt className="text-[length:var(--ecmp-font-overline-size)] uppercase tracking-wide text-ecmp-text-secondary">
                  {t("fieldCustomerPhone")}
                </dt>
                <dd className="text-ecmp-text-primary">{selected.phone}</dd>
              </div>
              <div>
                <dt className="text-[length:var(--ecmp-font-overline-size)] uppercase tracking-wide text-ecmp-text-secondary">
                  {t("fieldCustomerEmail")}
                </dt>
                <dd className="text-ecmp-text-primary">{selected.email}</dd>
              </div>
            </dl>
            <Button type="button" variant="ghost" onClick={onClear}>
              {t("changeCustomer")}
            </Button>
          </div>
        ) : (
          <>
            <div className="flex flex-col gap-2 sm:flex-row sm:items-end">
              <div className="min-w-0 flex-1">
                <Input
                  id="b3-customer-lookup"
                  name="customerLookup"
                  label={t("lookupLabel")}
                  description={t("lookupDescription")}
                  value={query}
                  onChange={(event) => {
                    setQuery(event.target.value);
                    setHits([]);
                  }}
                  onKeyDown={(event) => {
                    if (event.key === "Enter") {
                      event.preventDefault();
                      runSearch();
                    }
                  }}
                />
              </div>
              <Button type="button" variant="secondary" onClick={runSearch}>
                {t("lookupAction")}
              </Button>
            </div>
            {query.trim() && hits.length === 0 ? (
              <Alert tone="info" title={t("lookupEmpty")} />
            ) : null}
            {hits.length > 0 ? (
              <ul className="space-y-2">
                {hits.map((customer) => (
                  <li key={customer.ref}>
                    <button
                      type="button"
                      className="w-full rounded-[var(--ecmp-radius-md)] border border-ecmp-border/70 px-3 py-2 text-left transition hover:bg-ecmp-surface-sunken/50"
                      onClick={() => {
                        onSelect(customer);
                        setQuery("");
                        setHits([]);
                      }}
                    >
                      <span className="font-medium text-ecmp-text-primary">
                        {customer.name}
                      </span>
                      <span className="mt-0.5 block text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
                        {customer.ref} · {customer.phone}
                      </span>
                    </button>
                  </li>
                ))}
              </ul>
            ) : null}
          </>
        )}
      </CardBody>
    </Card>
  );
}
