import React from "react";

export function Card({ className = "", children, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={["rounded-xl border border-slate-200 bg-white shadow-card", className].join(" ")}
      {...props}
    >
      {children}
    </div>
  );
}

export function CardHeader({
  title,
  description,
  action,
  className = "",
}: {
  title: React.ReactNode;
  description?: React.ReactNode;
  action?: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={["flex items-start justify-between gap-4 border-b border-slate-100 px-5 py-4", className].join(" ")}>
      <div>
        <h3 className="text-sm font-semibold text-slate-900">{title}</h3>
        {description && <p className="mt-0.5 text-sm text-slate-500">{description}</p>}
      </div>
      {action}
    </div>
  );
}

export function CardBody({ className = "", children }: { className?: string; children: React.ReactNode }) {
  return <div className={["p-5", className].join(" ")}>{children}</div>;
}
