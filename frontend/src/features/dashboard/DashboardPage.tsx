import {
  BookOpen,
  CalendarClock,
  ChartSpline,
  ClipboardList,
  FileText,
  GraduationCap,
  NotebookPen,
  School,
  Users,
} from "lucide-react";

import { SectionTitle } from "@/components/common/SectionTitle";
import { APP_ENV } from "@/config/env";
import { useAssistant } from "@/hooks/useAssistant";
import type { StudentAttendanceEntry, StudentTimetableEntry } from "@/types";

import {
  ActionCard,
  ChartCard,
  MiniAreaChart,
  MiniLineChart,
  NotificationCard,
  ScheduleCard,
  StatisticCard,
} from "./DashboardCards";

const attendanceData = [
  { label: "W1", value: 89 },
  { label: "W2", value: 91 },
  { label: "W3", value: 90 },
  { label: "W4", value: 93 },
  { label: "W5", value: 92 },
];

const gpaData = [
  { label: "Sem 1", value: 3.2 },
  { label: "Sem 2", value: 3.4 },
  { label: "Sem 3", value: 3.5 },
  { label: "Sem 4", value: 3.7 },
  { label: "Sem 5", value: 3.8 },
];

const quickActions = [
  {
    title: "Attendance",
    description: "Explain my attendance.",
    icon: <Users className="h-5 w-5" />,
  },
  {
    title: "Timetable",
    description: "Show today's timetable.",
    icon: <CalendarClock className="h-5 w-5" />,
  },
  {
    title: "Transcript",
    description: "Show my transcript.",
    icon: <FileText className="h-5 w-5" />,
  },
  {
    title: "Courses",
    description: "Show my registered courses.",
    icon: <BookOpen className="h-5 w-5" />,
  },
  {
    title: "Policies",
    description: "What is the attendance policy?",
    icon: <School className="h-5 w-5" />,
  },
  {
    title: "Documents",
    description: "Show my academic documents.",
    icon: <NotebookPen className="h-5 w-5" />,
  },
];

const notifications = [
  { title: "Assignment uploaded", description: "A new assignment has been posted in Software Engineering." },
  { title: "Fee deadline", description: "Tuition fee deadline is approaching this Friday." },
  { title: "Attendance updated", description: "Your attendance record was updated for this week." },
  { title: "Registration opens", description: "Course registration opens next Monday at 9:00 AM." },
];

const semesterMarks = [
  { semester: "Semester 4", cgpa: "3.54", note: "Seeded data" },
  { semester: "Semester 5", cgpa: "3.71", note: "Seeded data" },
  { semester: "Semester 6", cgpa: "3.78", note: "Seeded data" },
];

interface DashboardPageProps {
  name: string;
  semester?: string | number | null;
  program?: string | null;
  cgpa?: number | null;
  attendancePercentage?: number | null;
  creditHours?: number | null;
  registeredCourses?: number | null;
  timetable?: StudentTimetableEntry[];
  attendanceRecords?: StudentAttendanceEntry[];
}

export function DashboardPage({
  name,
  semester,
  program,
  cgpa,
  attendancePercentage,
  creditHours,
  registeredCourses,
  timetable = [],
  attendanceRecords = [],
}: DashboardPageProps) {
  const { setDraftMessage, setMode } = useAssistant();
  const resolvedCgpa = cgpa ?? 3.78;
  const resolvedAttendance = attendancePercentage ?? 91;
  const resolvedCreditHours = creditHours ?? 18;
  const resolvedRegisteredCourses = registeredCourses ?? 6;
  const resolvedSemester = typeof semester === "number" ? `Semester ${semester}` : semester ?? "Semester 6";
  const resolvedProgram = program ?? "BSc Computer Science";
  const schedule = timetable.length
    ? timetable.map((item) => ({
        time: item.time,
        subject: item.course_name,
        room: item.room,
      }))
    : [
        { time: "09:00 - 10:30", subject: "Database Systems", room: "Room 204" },
        { time: "11:00 - 12:30", subject: "Software Engineering", room: "Lab 3" },
        { time: "02:00 - 03:30", subject: "AI Fundamentals", room: "Room 105" },
      ];

  const metrics = [
    { title: "CGPA", value: resolvedCgpa.toFixed(2), trend: "+0.12", icon: <GraduationCap className="h-5 w-5" /> },
    { title: "Current GPA", value: resolvedCgpa.toFixed(2), trend: "+0.08", icon: <ChartSpline className="h-5 w-5" /> },
    { title: "Attendance", value: `${resolvedAttendance.toFixed(0)}%`, trend: "+2%", icon: <Users className="h-5 w-5" /> },
    { title: "Credit Hours", value: String(resolvedCreditHours), trend: "On track", icon: <BookOpen className="h-5 w-5" /> },
    { title: "Registered Courses", value: String(resolvedRegisteredCourses), trend: "Stable", icon: <ClipboardList className="h-5 w-5" /> },
    { title: "Today's Classes", value: String(schedule.length), trend: "Current timetable", icon: <CalendarClock className="h-5 w-5" /> },
  ];

  function prefillAssistant(prompt: string): void {
    setDraftMessage(prompt);
    setMode("DOCKED");
  }

  return (
    <main className="space-y-8 py-8">
      <section className="grid gap-4">
        <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--muted)]">Student Dashboard</p>
        <h1 className="text-4xl font-semibold tracking-tight text-[var(--text)]">Good Morning, {name}</h1>
        <p className="max-w-2xl text-base text-[var(--muted)]">Welcome back to IM Copilot.</p>
        <div className="flex flex-wrap gap-3 text-sm text-[var(--muted)]">
          <span className="rounded-full border border-[var(--border)] bg-[var(--surface)] px-4 py-2">Semester: {resolvedSemester}</span>
          <span className="rounded-full border border-[var(--border)] bg-[var(--surface)] px-4 py-2">Program: {resolvedProgram}</span>
          <span className="rounded-full border border-[var(--border)] bg-[var(--surface)] px-4 py-2">
            {APP_ENV.demoMode ? "Demo mode with seeded data." : "Keep the momentum going today."}
          </span>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3 xl:grid-cols-6">
        {metrics.map((metric) => (
          <StatisticCard key={metric.title} {...metric} />
        ))}
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <ChartCard title="Attendance Overview">
          <div className="space-y-4">
            <p className="text-sm text-[var(--muted)]">
              Average attendance across enrolled courses. Individual course breakdown is shown below.
            </p>
            <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface-2)] p-4">
              <p className="text-sm text-[var(--muted)]">Overall attendance</p>
              <p className="mt-1 text-4xl font-semibold text-[var(--text)]">{resolvedAttendance.toFixed(0)}%</p>
              <p className="mt-2 text-xs text-[var(--muted)]">
                {attendancePercentage === undefined ? "Seeded frontend fallback." : "Loaded from your academic profile."}
              </p>
            </div>
            <div className="space-y-3">
              {(attendanceRecords.length
                ? attendanceRecords.map((item) => ({
                    course: item.course_name,
                    attendance: `${item.attendance_percentage.toFixed(0)}%`,
                  }))
                : [
                    { course: "Database Systems", attendance: "94%" },
                    { course: "Software Engineering", attendance: "91%" },
                    { course: "AI Fundamentals", attendance: "88%" },
                  ]
              ).map((course) => (
                <div key={course.course} className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-4">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold text-[var(--text)]">{course.course}</p>
                      <p className="text-xs text-[var(--muted)]">
                        {attendanceRecords.length > 0 ? "Loaded from academic profile" : "Seeded course breakdown"}
                      </p>
                    </div>
                    <span className="rounded-full bg-[var(--surface-2)] px-3 py-1 text-sm font-medium text-[var(--text)]">
                      {course.attendance}
                    </span>
                  </div>
                  <div className="mt-3 grid gap-2 text-sm text-[var(--muted)] sm:grid-cols-3">
                    <span>Mid Marks: 24/30</span>
                    <span>Assignment: 18/20</span>
                    <span>Final: N/A</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </ChartCard>

        <ChartCard title="Semester Marks Breakdown">
          <div className="space-y-3">
            <p className="text-sm text-[var(--muted)]">A separate area for semester-wise marks and DMCS breakdown can grow here later.</p>
            {semesterMarks.map((item) => (
              <div key={item.semester} className="flex items-center justify-between rounded-2xl border border-[var(--border)] bg-[var(--surface-2)] p-4">
                <div>
                  <p className="text-sm font-semibold text-[var(--text)]">{item.semester}</p>
                  <p className="text-xs text-[var(--muted)]">{item.note}</p>
                </div>
                <p className="text-lg font-semibold text-[var(--text)]">{item.cgpa}</p>
              </div>
            ))}
          </div>
        </ChartCard>
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <ChartCard title="Attendance Trend">
          <MiniLineChart data={attendanceData} />
        </ChartCard>
        <ChartCard title="Semester GPA Trend">
          <MiniAreaChart data={gpaData} />
        </ChartCard>
      </section>

      <section className="space-y-4">
        <SectionTitle title="Quick Actions" description="Open the most common student tasks from one clean grid." />
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {quickActions.map((action) => (
            <ActionCard key={action.title} {...action} onClick={() => prefillAssistant(action.description)} />
          ))}
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <div id="schedule-section">
          <ScheduleCard items={schedule} />
        </div>
        <div id="notifications-section" className="space-y-4">
          <SectionTitle title="Notifications" description="Seeded notices for the dashboard experience." />
          <div className="space-y-3">
            {notifications.map((item) => (
              <NotificationCard key={item.title} item={item} />
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
