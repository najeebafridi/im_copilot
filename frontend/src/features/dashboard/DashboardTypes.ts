import { type ReactNode } from "react";

export interface DashboardMetric {
  title: string;
  value: string;
  trend: string;
  icon: ReactNode;
}

export interface DashboardAction {
  title: string;
  description: string;
  icon: ReactNode;
  assistantContext?: {
    page: string;
    widget: string;
    source: string;
  };
  onClick?: () => void;
}

export interface DashboardScheduleItem {
  time: string;
  subject: string;
  room: string;
  instructor: string;
}

export interface DashboardNotificationItem {
  title: string;
  description: string;
}
