"use client";

import {
  useCallback,
  useEffect,
  useState,
  type ChangeEvent,
  type FormEvent,
} from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  createComplaint,
  fetchBranches,
  fetchCustomers,
  uploadAttachment,
  type Branch,
  type Customer,
} from "@/lib/api";
import {
  Alert,
  Button,
  Card,
  CardBody,
  CardDescription,
  CardHeader,
  CardTitle,
  Empty,
  Input,
  PageContainer,
  PageHeader,
  Select,
  Textarea,
} from "@/shared/ui";
import {
  CHANNEL_OPTIONS,
  createEmptyComplaintForm,
  PRIORITY_OPTIONS,
  toCreateComplaintRequest,
  validateCreateComplaintForm,
  type CreateComplaintFieldErrors,
  type CreateComplaintFormValues,
} from "./createComplaintForm";

export function CreateComplaintView() {
  const router = useRouter();
  const { user, hasPermission } = useAuth();
  const canCreate = hasPermission("complaints:create");
  const agentBranchId = user?.branchId ?? null;

  const [values, setValues] = useState<CreateComplaintFormValues>(() =>
    createEmptyComplaintForm({ branchId: agentBranchId }),
  );
  const [errors, setErrors] = useState<CreateComplaintFieldErrors>({});
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [customersLoading, setCustomersLoading] = useState(true);
  const [customersError, setCustomersError] = useState<string | null>(null);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [branchesLoading, setBranchesLoading] = useState(true);
  const [branchesError, setBranchesError] = useState<string | null>(null);
  const [files, setFiles] = useState<File[]>([]);

  useEffect(() => {
    if (!canCreate) {
      setCustomersLoading(false);
      return;
    }
    let cancelled = false;
    (async () => {
      setCustomersLoading(true);
      setCustomersError(null);
      try {
        const res = await fetchCustomers(100);
        if (!cancelled) setCustomers(res.data);
      } catch (err) {
        if (!cancelled) {
          setCustomersError(
            err instanceof ApiError
              ? err.message
              : "Unable to load customers.",
          );
        }
      } finally {
        if (!cancelled) setCustomersLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [canCreate]);

  useEffect(() => {
    if (!canCreate) {
      setBranchesLoading(false);
      return;
    }
    let cancelled = false;
    (async () => {
      setBranchesLoading(true);
      setBranchesError(null);
      try {
        const res = await fetchBranches(100);
        if (!cancelled) {
          setBranches(res.data);
          if (agentBranchId) {
            const match = res.data.find((b) => b.id === agentBranchId);
            if (match) {
              setValues((prev) =>
                prev.branchId ? prev : { ...prev, branchId: match.id },
              );
            }
          }
        }
      } catch (err) {
        if (!cancelled) {
          setBranchesError(
            err instanceof ApiError
              ? err.message
              : "Unable to load branches.",
          );
        }
      } finally {
        if (!cancelled) setBranchesLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [agentBranchId, canCreate]);

  if (!canCreate) {
    return (
      <PageContainer className="space-y-6">
        <PageHeader
          title="Create Complaint"
          breadcrumbs={[
            { label: "Home", href: "/dashboard" },
            { label: "Complaints", href: "/complaints" },
            { label: "Create" },
          ]}
        />
        <Empty
          title="Access restricted"
          description="You need the complaints:create permission to register a complaint."
          action={
            <Button
              type="button"
              variant="outline"
              onClick={() => router.push("/complaints")}
            >
              Back to Complaints
            </Button>
          }
        />
      </PageContainer>
    );
  }

  const updateField = useCallback(
    <K extends keyof CreateComplaintFormValues>(
      key: K,
      value: CreateComplaintFormValues[K],
    ) => {
      setValues((prev) => ({ ...prev, [key]: value }));
      setErrors((prev) => {
        if (!prev[key]) return prev;
        const next = { ...prev };
        delete next[key];
        return next;
      });
    },
    [],
  );

  function onTextChange(
    key: keyof CreateComplaintFormValues,
  ): (
    event: ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >,
  ) => void {
    return (event) => {
      updateField(
        key,
        event.target.value as CreateComplaintFormValues[typeof key],
      );
    };
  }

  function onCustomerChange(event: ChangeEvent<HTMLSelectElement>): void {
    const customerId = event.target.value;
    const match = customers.find((c) => c.id === customerId);
    setValues((prev) => ({
      ...prev,
      customerId,
      customerName: match?.fullName ?? "",
    }));
    setErrors((prev) => {
      const next = { ...prev };
      delete next.customerId;
      delete next.customerName;
      return next;
    });
  }

  function onCancel(): void {
    router.push("/complaints");
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setSubmitError(null);

    const nextErrors = validateCreateComplaintForm(values);
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length > 0) {
      const firstKey = Object.keys(nextErrors)[0];
      const el = firstKey ? document.getElementById(firstKey) : null;
      el?.focus();
      return;
    }

    setSubmitting(true);
    try {
      const response = await createComplaint(toCreateComplaintRequest(values));
      const complaintId = response.data.id;

      const failedUploads: string[] = [];
      for (const file of files) {
        try {
          await uploadAttachment("Complaint", complaintId, file);
        } catch {
          // Best-effort: complaint already exists; user can retry from detail.
          failedUploads.push(file.name);
        }
      }

      if (failedUploads.length > 0) {
        router.push(
          `/complaints/${complaintId}?attachmentUploadFailed=${failedUploads.length}`,
        );
      } else {
        router.push(`/complaints/${complaintId}`);
      }
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Unable to create complaint.";
      setSubmitError(message);
    } finally {
      setSubmitting(false);
    }
  }

  const customerOptions = customers.map((c) => ({
    value: c.id,
    label: `${c.fullName} (${c.externalCustomerId})`,
  }));

  const branchOptions = branches.map((b) => ({
    value: b.id,
    label: b.name,
  }));

  return (
    <PageContainer className="space-y-6">
      <PageHeader
        title="Create Complaint"
        breadcrumbs={[
          { label: "Home", href: "/dashboard" },
          { label: "Complaints", href: "/complaints" },
          { label: "Create" },
        ]}
        description="Register a new complaint. Required fields are marked with an asterisk."
      />

      <form
        noValidate
        onSubmit={(event) => void onSubmit(event)}
        aria-label="Create complaint form"
        className="space-y-6"
      >
        {submitError ? (
          <Alert
            tone="danger"
            title="Could not create complaint"
            description={submitError}
          />
        ) : null}

        {customersError ? (
          <Alert
            tone="danger"
            title="Could not load customers"
            description={customersError}
          />
        ) : null}

        {branchesError ? (
          <Alert
            tone="danger"
            title="Could not load branches"
            description={branchesError}
          />
        ) : null}

        <Card>
          <CardHeader>
            <CardTitle id="section-customer-info">
              Customer Information
            </CardTitle>
            <CardDescription>
              Select a customer from the local reference list. Customer ID is
              taken from that selection.
            </CardDescription>
          </CardHeader>
          <CardBody>
            <fieldset
              aria-labelledby="section-customer-info"
              className="grid grid-cols-1 gap-4 md:grid-cols-2"
            >
              <legend className="sr-only">Customer Information</legend>
              <Select
                name="customerId"
                id="customerId"
                label="Customer"
                required
                placeholder={
                  customersLoading ? "Loading customers…" : "Select customer"
                }
                options={customerOptions}
                value={values.customerId}
                onChange={onCustomerChange}
                error={errors.customerId || errors.customerName}
                disabled={customersLoading || customerOptions.length === 0}
                aria-required="true"
                hint={
                  customerOptions.length === 0 && !customersLoading
                    ? "No customers available in the reference list"
                    : "Loaded from GET /api/v1/customers"
                }
              />
              <Input
                name="customerName"
                id="customerName"
                label="Customer name"
                value={values.customerName}
                readOnly
                aria-readonly="true"
                hint="Filled from the selected customer"
              />
            </fieldset>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle id="section-complaint-info">
              Complaint Information
            </CardTitle>
            <CardDescription>
              Subject, narrative, and priority for the case.
            </CardDescription>
          </CardHeader>
          <CardBody>
            <fieldset
              aria-labelledby="section-complaint-info"
              className="grid grid-cols-1 gap-4 md:grid-cols-2"
            >
              <legend className="sr-only">Complaint Information</legend>
              <div className="md:col-span-2">
                <Input
                  name="subject"
                  id="subject"
                  label="Subject"
                  required
                  maxLength={200}
                  value={values.subject}
                  onChange={onTextChange("subject")}
                  error={errors.subject}
                  aria-required="true"
                  autoComplete="off"
                />
              </div>
              <Select
                name="priority"
                id="priority"
                label="Priority"
                required
                placeholder="Select priority"
                options={PRIORITY_OPTIONS}
                value={values.priority}
                onChange={onTextChange("priority")}
                error={errors.priority}
                aria-required="true"
              />
              <div className="md:col-span-2">
                <Textarea
                  name="description"
                  id="description"
                  label="Description"
                  required
                  rows={5}
                  maxLength={5000}
                  value={values.description}
                  onChange={onTextChange("description")}
                  error={errors.description}
                  aria-required="true"
                  hint={`${values.description.trim().length}/5000`}
                />
              </div>
            </fieldset>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle id="section-location">Location</CardTitle>
            <CardDescription>
              Select the branch where the complaint applies. The UUID is taken
              from that selection.
            </CardDescription>
          </CardHeader>
          <CardBody>
            <fieldset
              aria-labelledby="section-location"
              className="grid grid-cols-1 gap-4 md:grid-cols-2"
            >
              <legend className="sr-only">Location</legend>
              <Select
                name="branchId"
                id="branchId"
                label="Branch"
                required
                placeholder={
                  branchesLoading ? "Loading branches…" : "Select branch"
                }
                options={branchOptions}
                value={values.branchId}
                onChange={onTextChange("branchId")}
                error={errors.branchId}
                disabled={branchesLoading || branchOptions.length === 0}
                aria-required="true"
                hint={
                  branchOptions.length === 0 && !branchesLoading
                    ? "No active branches available"
                    : "Loaded from GET /api/v1/branches"
                }
              />
            </fieldset>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle id="section-additional">
              Additional Information
            </CardTitle>
            <CardDescription>
              Channel, category, and reported time when known.
            </CardDescription>
          </CardHeader>
          <CardBody>
            <fieldset
              aria-labelledby="section-additional"
              className="grid grid-cols-1 gap-4 md:grid-cols-2"
            >
              <legend className="sr-only">Additional Information</legend>
              <Select
                name="channel"
                id="channel"
                label="Channel"
                placeholder="Select channel (optional)"
                options={CHANNEL_OPTIONS}
                value={values.channel}
                onChange={onTextChange("channel")}
                error={errors.channel}
              />
              <Input
                name="category"
                id="category"
                label="Category"
                maxLength={64}
                value={values.category}
                onChange={onTextChange("category")}
                error={errors.category}
                autoComplete="off"
              />
              <Input
                name="reportedAt"
                id="reportedAt"
                type="datetime-local"
                label="Reported at"
                value={values.reportedAt}
                onChange={onTextChange("reportedAt")}
                error={errors.reportedAt}
                hint="Defaults to today; change if reported at another time"
              />
            </fieldset>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle id="section-attachments">Attachments</CardTitle>
            <CardDescription>
              Optional files are uploaded after the complaint is created
              (API-323).
            </CardDescription>
          </CardHeader>
          <CardBody className="space-y-3">
            <Input
              type="file"
              name="attachments"
              id="attachments"
              label="Attach files"
              multiple
              onChange={(event) => {
                const list = event.target.files
                  ? Array.from(event.target.files)
                  : [];
                setFiles(list);
              }}
              hint={
                files.length === 0
                  ? "You can add more files later from the complaint detail page."
                  : `${files.length} file(s) selected`
              }
            />
          </CardBody>
        </Card>

        <div className="flex flex-col-reverse gap-3 border-t border-ecmp-border pt-4 sm:flex-row sm:justify-end">
          <Button
            type="button"
            variant="outline"
            onClick={onCancel}
            disabled={submitting}
            aria-label="Cancel and return to complaints"
          >
            Cancel
          </Button>
          <Button
            type="submit"
            loading={submitting}
            aria-label="Create complaint"
          >
            {submitting ? "Creating…" : "Create Complaint"}
          </Button>
        </div>
      </form>
    </PageContainer>
  );
}
