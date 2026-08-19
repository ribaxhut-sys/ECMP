import { Badge } from "@/shared/ui";

export function ReasonPresetTags({
  presets,
  onSelect,
}: {
  presets: string[];
  onSelect: (preset: string) => void;
}) {
  if (presets.length === 0) return null;
  return (
    <div className="flex flex-wrap gap-2">
      {presets.map((preset) => (
        <button key={preset} type="button" onClick={() => onSelect(preset)}>
          <Badge tone="neutral" variant="outline" className="cursor-pointer">
            {preset}
          </Badge>
        </button>
      ))}
    </div>
  );
}
