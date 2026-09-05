import React from "react";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  icon?: React.ReactNode;
  error?: boolean;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(function Input(
  { icon, error, className = "", ...props },
  ref
) {
  return (
    <div className="relative">
      {icon && (
        <span className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
          {icon}
        </span>
      )}
      <input
        ref={ref}
        className={[
          "block w-full rounded-lg border bg-white text-sm text-slate-900 shadow-xs transition-colors",
          "placeholder:text-slate-400",
          "focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20",
          error ? "border-red-300" : "border-slate-300",
          icon ? "pl-9 pr-3 py-2" : "px-3 py-2",
          className,
        ].join(" ")}
        {...props}
      />
    </div>
  );
});

export function Label({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return <label className={["mb-1.5 block text-sm font-medium text-slate-700", className].join(" ")}>{children}</label>;
}

export function HelperText({ children }: { children: React.ReactNode }) {
  return <p className="mt-1.5 text-xs text-slate-400">{children}</p>;
}
