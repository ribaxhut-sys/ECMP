import { Badge } from "@/shared/ui/badge";

/**
 * Menggabungkan preset ke teks yang sudah ada, bukan menimpanya.
 * Preset yang sudah ada di teks tidak ditambahkan dua kali.
 */
export function appendPreset(current: string, preset: string): string {
  const base = current.trimEnd();
  if (base.length === 0) return preset;
  const alreadyThere = base
    .split("\n")
    .some((line) => line.trim() === preset.trim());
  if (alreadyThere) return current;
  return `${base}\n${preset}`;
}

/**
 * Quick-fill chips for a free-text field. Clicking a chip appends the preset on
 * a new line, keeping whatever the user already wrote; the presets themselves
 * come from PUBLIC settings (`*_presets`, JSON string array) via
 * `useReasonPresets`. `onSelect` receives the complete next field value.
 */
export function ReasonPresetTags({
  presets,
  value,
  onSelect,
}: {
  presets: string[];
  value: string;
  onSelect: (nextValue: string) => void;
}) {
  if (presets.length === 0) return null;
  return (
    <div className="flex flex-wrap gap-2">
      {presets.map((preset) => (
        <button
          key={preset}
          type="button"
          onClick={() => onSelect(appendPreset(value, preset))}
        >
          <Badge tone="neutral" variant="outline" className="cursor-pointer">
            {preset}
          </Badge>
        </button>
      ))}
    </div>
  );
}
