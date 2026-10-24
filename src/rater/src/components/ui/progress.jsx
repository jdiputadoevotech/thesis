import { cn } from "../../lib/utils.js";

export function Progress({ value = 0, className }) {
  const clamped = Math.max(0, Math.min(100, value));
  return (
    <div className={cn("relative h-2 w-full overflow-hidden rounded-full bg-slate-100", className)}>
      <div
        className="h-full bg-slate-900 transition-all duration-300 ease-out"
        style={{ width: `${clamped}%` }}
      />
    </div>
  );
}

export function Separator({ className, orientation = "horizontal", ...props }) {
  return (
    <div
      className={cn(
        "shrink-0 bg-slate-200",
        orientation === "horizontal" ? "h-[1px] w-full" : "h-full w-[1px]",
        className,
      )}
      {...props}
    />
  );
}

export function TabsList({ className, ...props }) {
  return (
    <div
      className={cn(
        "inline-flex h-9 items-center justify-center rounded-lg bg-slate-100 p-1 text-slate-600",
        className,
      )}
      {...props}
    />
  );
}

export function TabsTrigger({ active, className, ...props }) {
  return (
    <button
      type="button"
      className={cn(
        "inline-flex items-center justify-center whitespace-nowrap rounded-md px-3 py-1 text-xs font-medium transition-all cursor-pointer select-none",
        active ? "bg-white text-slate-950 shadow-2xs" : "text-slate-600 hover:text-slate-900",
        className,
      )}
      {...props}
    />
  );
}
