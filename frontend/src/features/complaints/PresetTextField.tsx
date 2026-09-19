"use client";

import { useRef, type ComponentProps } from "react";
import { ReasonPresetTags } from "@/shared/ui";
import {
  KnowledgeMentionTextarea,
  type KnowledgeMentionTextareaHandle,
} from "./KnowledgeMentionTextarea";

type MentionFieldProps = Omit<
  ComponentProps<typeof KnowledgeMentionTextarea>,
  "ref"
>;

/**
 * A mention textarea with its quick-fill preset tags on top. Clicking a tag
 * appends the preset to whatever the user already wrote (never overwrites) and
 * returns the caret to the end of the text so typing can continue right away.
 * An empty `presets` array renders the field alone.
 */
export function PresetTextField({
  presets,
  value,
  onChange,
  ...field
}: MentionFieldProps & { presets: string[] }) {
  const fieldRef = useRef<KnowledgeMentionTextareaHandle | null>(null);
  return (
    <>
      <ReasonPresetTags
        presets={presets}
        value={value}
        onSelect={(next) => {
          const changed = next !== value;
          if (changed) onChange(next);
          fieldRef.current?.focusEnd({ afterValueSync: changed });
        }}
      />
      <KnowledgeMentionTextarea
        {...field}
        value={value}
        onChange={onChange}
        ref={fieldRef}
      />
    </>
  );
}
