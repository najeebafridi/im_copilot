import { type AuthRole } from "@/types";

export const PERMISSIONS = {
  guestPolicyChat: "guest_policy_chat",
  studentDashboard: "student_dashboard",
  studentChat: "student_chat",
  studentAcademicRecords: "student_academic_records",
  adminDashboard: "admin_dashboard",
  adminUploadDocuments: "admin_upload_documents",
  adminStudentRecords: "admin_student_records",
  adminLogs: "admin_logs",
} as const;

export type Permission = (typeof PERMISSIONS)[keyof typeof PERMISSIONS];

const ROLE_PERMISSIONS: Record<AuthRole, Permission[]> = {
  student: [PERMISSIONS.studentDashboard, PERMISSIONS.studentChat, PERMISSIONS.studentAcademicRecords],
  admin: [
    PERMISSIONS.adminDashboard,
    PERMISSIONS.adminUploadDocuments,
    PERMISSIONS.adminStudentRecords,
    PERMISSIONS.adminLogs,
  ],
};

export function hasPermission(role: AuthRole | null, permission: Permission): boolean {
  if (!role) {
    return false;
  }
  return ROLE_PERMISSIONS[role].includes(permission);
}
