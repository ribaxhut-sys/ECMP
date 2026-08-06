"use client";

import { useTranslations } from "next-intl";
import { Input, Select, Textarea } from "@/shared/ui";
import {
  MOCK_CATEGORIES,
  MOCK_CHANNELS,
  MOCK_PRIORITIES,
  type MockCategory,
  type MockChannel,
  type MockPriority,
} from "@/features/supervisor-assign/mock/assignmentRepository";

export interface IntakeFormFieldsProps {
  subject: string;
  description: string;
  category: MockCategory | "";
  channel: MockChannel | "";
  priority: MockPriority | "";
  disabled?: boolean;
  errors?: Partial<
    Record<"subject" | "description" | "category" | "channel" | "priority", string>
  >;
  onChange: (patch: {
    subject?: string;
    description?: string;
    category?: MockCategory | "";
    channel?: MockChannel | "";
    priority?: MockPriority | "";
  }) => void;
}

/** Middle form — subject / description / category / channel / priority (SCR-WS-01). */
export function IntakeFormFields({
  subject,
  description,
  category,
  channel,
  priority,
  disabled,
  errors,
  onChange,
}: IntakeFormFieldsProps) {
  const t = useTranslations("intake");

  return (
    <div className="space-y-4">
      <Input
        id="b3-subject"
        name="subject"
        label={t("fieldSubject")}
        required
        disabled={disabled}
        value={subject}
        error={errors?.subject}
        onChange={(event) => onChange({ subject: event.target.value })}
      />
      <Textarea
        id="b3-description"
        name="description"
        label={t("fieldDescription")}
        required
        disabled={disabled}
        rows={4}
        value={description}
        error={errors?.description}
        onChange={(event) => onChange({ description: event.target.value })}
      />
      <div className="grid gap-4 sm:grid-cols-3">
        <Select
          id="b3-category"
          name="category"
          label={t("fieldCategory")}
          required
          disabled={disabled}
          value={category}
          error={errors?.category}
          placeholder={t("selectPlaceholder")}
          options={MOCK_CATEGORIES.map((value) => ({
            value,
            label: t(`category.${value}`),
          }))}
          onChange={(event) =>
            onChange({ category: event.target.value as MockCategory | "" })
          }
        />
        <Select
          id="b3-channel"
          name="channel"
          label={t("fieldChannel")}
          required
          disabled={disabled}
          value={channel}
          error={errors?.channel}
          placeholder={t("selectPlaceholder")}
          options={MOCK_CHANNELS.map((value) => ({
            value,
            label: t(`channel.${value}`),
          }))}
          onChange={(event) =>
            onChange({ channel: event.target.value as MockChannel | "" })
          }
        />
        <Select
          id="b3-priority"
          name="priority"
          label={t("fieldPriority")}
          required
          disabled={disabled}
          value={priority}
          error={errors?.priority}
          placeholder={t("selectPlaceholder")}
          options={MOCK_PRIORITIES.map((value) => ({
            value,
            label: t(`priority.${value}`),
          }))}
          onChange={(event) =>
            onChange({ priority: event.target.value as MockPriority | "" })
          }
        />
      </div>
    </div>
  );
}
