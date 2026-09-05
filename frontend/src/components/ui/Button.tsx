import { Loader2 } from "lucide-react";
import React from "react";

type Variant = "primary" | "secondary" | "ghost" | "danger";
type Size = "sm" | "md" | "lg";

const VARIANT_CLASSES: Record<Variant, string> = {
  primary:
    "bg-brand-600 text-white shadow-xs hover:bg-brand-700 active:bg-brand-800 disabled:bg-brand-300",
  secondary:
    "bg-white text-slate-700 border border-slate-300 shadow-xs hover:bg-slate-50 active:bg-slate-100 disabled:text-slate-400",
  ghost: "text-slate-600 hover:bg-slate-100 active:bg-slate-200 disabled:text-slate-300",
  danger: "bg-red-600 text-white shadow-xs hover:bg-red-700 active:bg-red-800 disabled:bg-red-300",
};

const SIZE_CLASSES: Record<Size, string> = {
  sm: "h-8 px-3 text-xs gap-1.5",
  md: "h-9 px-4 text-sm gap-2",
  lg: "h-11 px-5 text-sm gap-2",
};

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  loading?: boolean;
  icon?: React.ReactNode;
}

export function Button({
  variant = "primary",
  size = "md",
  loading = false,
  icon,
  disabled,
  className = "",
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      disabled={disabled || loading}
      className={[
        "inline-flex items-center justify-center rounded-lg font-semibold transition-colors",
        "disabled:cursor-not-allowed",
        VARIANT_CLASSES[variant],
        SIZE_CLASSES[size],
        className,
      ].join(" ")}
      {...props}
    >
      {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : icon}
      {children}
    </button>
  );
}
