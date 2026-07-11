import { apiClient } from "./apiClient";

import { type AuthLoginRequest, type AuthSession, type UserProfile } from "@/types";
import { isAxiosError } from "axios";

interface LoginResponse {
  access_token: string;
  token_type: string;
}

interface BackendUserProfile {
  student_id: string;
  name: string;
  role: "student" | "admin";
  program?: string | null;
  semester?: number | null;
  cgpa?: number | null;
  attendance_percentage?: number | null;
  credit_hours?: number | null;
  registered_courses?: number | null;
  timetable?: Array<{
    course_name: string;
    day: string;
    time: string;
    room: string;
  }>;
  attendance_records?: Array<{
    course_name: string;
    attendance_percentage: number;
  }>;
}

function normalizeUserProfile(response: BackendUserProfile): UserProfile {
  return {
    id: response.student_id,
    name: response.name,
    role: response.role,
    program: response.program ?? null,
    semester: response.semester ?? null,
    cgpa: response.cgpa ?? null,
    attendancePercentage: response.attendance_percentage ?? null,
    creditHours: response.credit_hours ?? null,
    registeredCourses: response.registered_courses ?? null,
    timetable: response.timetable ?? [],
    attendanceRecords: response.attendance_records ?? [],
  };
}

function buildLoginBody(request: AuthLoginRequest): URLSearchParams | Record<string, string> {
  if (request.mode === "admin") {
    return new URLSearchParams({
      username: request.identifier,
      password: request.password,
    });
  }

  return {
    student_id: request.identifier,
    password: request.password,
  };
}

export async function login(request: AuthLoginRequest): Promise<AuthSession> {
  try {
    const response = await apiClient.post<LoginResponse>("/api/v1/auth/login", buildLoginBody(request), {
      headers:
        request.mode === "admin"
          ? { "Content-Type": "application/x-www-form-urlencoded" }
          : undefined,
    });

    const token = response.data.access_token;
    const user = await getCurrentUser(token);
    return { token, user };
  } catch (error) {
    if (isAxiosError(error)) {
      if (!error.response) {
        throw new Error("Cannot reach the backend server. Start the backend on port 8000.");
      }
      const detail = error.response?.data;
      if (typeof detail === "object" && detail !== null && "detail" in detail && typeof detail.detail === "string") {
        throw new Error(detail.detail);
      }
      if (typeof detail === "string") {
        throw new Error(detail);
      }
    }
    throw new Error("Login failed.");
  }
}

export async function getCurrentUser(token?: string): Promise<UserProfile> {
  try {
    const response = await apiClient.get<BackendUserProfile>("/api/v1/auth/me", {
      headers: token ? { Authorization: `Bearer ${token}` } : undefined,
    });
    return normalizeUserProfile(response.data);
  } catch {
    throw new Error("Cannot reach the backend server. Start the backend on port 8000.");
  }
}

export async function logout(): Promise<void> {
  return Promise.resolve();
}
