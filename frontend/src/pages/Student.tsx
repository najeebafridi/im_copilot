import { useAuth } from "@/hooks/useAuth";
import { DashboardPage } from "@/features/dashboard/DashboardPage";
import { AssistantPlaceholder } from "@/features/chat/AssistantPlaceholder";

export function Student() {
  const auth = useAuth();

  return (
    <>
      <DashboardPage
        name={auth.user?.name ?? "Student"}
        semester={auth.user?.semester ?? "Semester 6"}
        program={auth.user?.program ?? "BSc Computer Science"}
        cgpa={auth.user?.cgpa ?? null}
        attendancePercentage={auth.user?.attendancePercentage ?? null}
        creditHours={auth.user?.creditHours ?? null}
        registeredCourses={auth.user?.registeredCourses ?? null}
        timetable={auth.user?.timetable ?? []}
        attendanceRecords={auth.user?.attendanceRecords ?? []}
      />
      <AssistantPlaceholder />
    </>
  );
}
