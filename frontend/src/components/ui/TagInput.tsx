import { X } from "lucide-react";
import React, { useState } from "react";

/**
 * Chip-style editor for a string[] field (e.g. brand keywords, hashtags).
 * Enter or comma commits the current word as a tag; Backspace on an empty
 * field removes the last tag.
 */
export function TagInput({
  value,
  onChange,
  placeholder,
}: {
  value: string[];
  onChange: (next: string[]) => void;
  placeholder?: string;
}) {
  const [draft, setDraft] = useState("");

  const commit = (raw: string) => {
    const tag = raw.trim();
    if (tag && !value.includes(tag)) onChange([...value, tag]);
    setDraft("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      commit(draft);
    } else if (e.key === "Backspace" && draft === "" && value.length > 0) {
      onChange(value.slice(0, -1));
    }
  };

  return (
    <div className="flex min-h-[42px] flex-wrap items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-2.5 py-1.5 shadow-xs transition-colors focus-within:border-brand-500 focus-within:ring-2 focus-within:ring-brand-500/20">
      {value.map((tag) => (
        <span
          key={tag}
          className="inline-flex items-center gap-1 rounded-md bg-brand-50 py-1 pl-2 pr-1 text-xs font-medium text-brand-700 ring-1 ring-inset ring-brand-200"
        >
          {tag}
          <button
            type="button"
            onClick={() => onChange(value.filter((t) => t !== tag))}
            className="rounded p-0.5 text-brand-500 hover:bg-brand-100 hover:text-brand-800"
            aria-label={`Remove ${tag}`}
          >
            <X className="h-3 w-3" />
          </button>
        </span>
      ))}
      <input
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        onKeyDown={handleKeyDown}
        onBlur={() => draft && commit(draft)}
        placeholder={value.length === 0 ? placeholder : undefined}
        className="min-w-[8ch] flex-1 border-none bg-transparent py-0.5 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-0"
      />
    </div>
  );
}
