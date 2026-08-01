import type { ReactNode } from "react";

type StatusKind = "success" | "error" | "info";

export function StatusBanner({
  kind,
  title,
  children,
}: {
  kind: StatusKind;
  title: string;
  children?: ReactNode;
}) {
  const palette = {
    success: "border-emerald-300 bg-emerald-50 text-emerald-700",
    error: "border-rose-300 bg-rose-50 text-rose-700",
    info: "border-slate-300 bg-slate-50 text-slate-700",
  }[kind];

  return (
    <div className={`rounded-2xl border px-4 py-3 ${palette}`}>
      <p className="font-semibold">{title}</p>
      {children ? <div className="mt-1 text-sm">{children}</div> : null}
    </div>
  );
}
