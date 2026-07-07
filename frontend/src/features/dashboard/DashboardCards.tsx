import type { ReactNode } from "react";
import { ArrowUpRight } from "lucide-react";
import { Area, AreaChart, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { Card } from "@/components/ui/Card";
import type { DashboardAction, DashboardMetric, DashboardNotificationItem, DashboardScheduleItem } from "./DashboardTypes";

interface StatisticCardProps extends DashboardMetric {}
interface ActionCardProps extends DashboardAction {}

export function StatisticCard({ title, value, trend, icon }: StatisticCardProps) {
  return (
    <Card className="group p-4 transition-all hover:-translate-y-[2px] hover:shadow-xl">
      <div className="flex items-start justify-between gap-3">
        <div className="space-y-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[var(--surface-2)] text-[var(--text)]">
            {icon}
          </div>
          <div>
            <p className="text-sm text-[var(--muted)]">{title}</p>
            <p className="mt-1 text-3xl font-semibold text-[var(--text)]">{value}</p>
          </div>
        </div>
        <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2.5 py-1 text-[11px] font-medium text-emerald-700">
          <ArrowUpRight className="h-3 w-3" />
          {trend}
        </span>
      </div>
    </Card>
  );
}

export function ActionCard({ title, description, icon, onClick }: ActionCardProps) {
  return (
    <button type="button" className="group text-left" aria-label={title} onClick={onClick}>
      <Card className="h-full p-5 transition-all hover:-translate-y-[2px] hover:shadow-xl">
        <div className="flex items-start gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[var(--accent)] text-white">
            {icon}
          </div>
          <div className="min-w-0">
            <p className="text-base font-semibold text-[var(--text)]">{title}</p>
            <p className="mt-1 text-sm leading-6 text-[var(--muted)]">{description}</p>
          </div>
        </div>
      </Card>
    </button>
  );
}

export function ChartCard({ title, children }: { title: string; children: ReactNode }) {
  return (
    <Card className="p-5">
      <div className="mb-4">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-[var(--muted)]">{title}</p>
      </div>
      {children}
    </Card>
  );
}

export function ScheduleCard({ items }: { items: DashboardScheduleItem[] }) {
  return (
    <Card className="p-5">
      <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-[var(--muted)]">Today's Schedule</h3>
      <div className="mt-4 space-y-3">
        {items.map((item) => (
          <div key={`${item.time}-${item.subject}`} className="rounded-2xl border border-[var(--border)] bg-[var(--surface-2)] p-4">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="text-sm font-semibold text-[var(--text)]">{item.subject}</p>
                <p className="text-sm text-[var(--muted)]">
                  {item.room} · {item.instructor}
                </p>
              </div>
              <span className="rounded-full bg-[var(--surface)] px-3 py-1 text-xs font-medium text-[var(--text)]">
                {item.time}
              </span>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}

export function NotificationCard({ item }: { item: DashboardNotificationItem }) {
  return (
    <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-4 transition-all hover:-translate-y-[2px] hover:shadow-md">
      <p className="text-sm font-semibold text-[var(--text)]">{item.title}</p>
      <p className="mt-1 text-sm text-[var(--muted)]">{item.description}</p>
    </div>
  );
}

export function MiniLineChart({ data }: { data: Array<{ label: string; value: number }> }) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <LineChart data={data}>
        <XAxis dataKey="label" tickLine={false} axisLine={false} stroke="var(--muted)" fontSize={12} />
        <YAxis tickLine={false} axisLine={false} stroke="var(--muted)" fontSize={12} />
        <Tooltip />
        <Line type="monotone" dataKey="value" stroke="var(--accent)" strokeWidth={3} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}

export function MiniAreaChart({ data }: { data: Array<{ label: string; value: number }> }) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <AreaChart data={data}>
        <XAxis dataKey="label" tickLine={false} axisLine={false} stroke="var(--muted)" fontSize={12} />
        <YAxis tickLine={false} axisLine={false} stroke="var(--muted)" fontSize={12} />
        <Tooltip />
        <Area type="monotone" dataKey="value" stroke="var(--accent)" fill="var(--surface-3)" />
      </AreaChart>
    </ResponsiveContainer>
  );
}
