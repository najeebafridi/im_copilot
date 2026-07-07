import { Route, Routes } from "react-router-dom";

import { AdminLayout } from "@/layouts/AdminLayout";
import { MainLayout } from "@/layouts/MainLayout";
import { AdminLogin } from "@/features/auth/AdminLogin";
import { Admin } from "@/pages/Admin";
import { Guest } from "@/pages/Guest";
import { Landing } from "@/pages/Landing";
import { Login } from "@/pages/Login";
import { NotFound } from "@/pages/NotFound";
import { Student } from "@/pages/Student";
import { APP_ROUTES } from "@/config/routes";
import { ProtectedRoute } from "./ProtectedRoute";
import { PublicRoute } from "./PublicRoute";

export function AppRoutes() {
  return (
    <Routes>
      <Route element={<PublicRoute />}>
        <Route path={APP_ROUTES.landing} element={<Landing />} />
        <Route path={APP_ROUTES.login} element={<Login />} />
        <Route path={APP_ROUTES.adminLogin} element={<AdminLogin />} />
      </Route>
      <Route element={<MainLayout />}>
        <Route path={APP_ROUTES.guest} element={<Guest />} />
      </Route>
      <Route element={<ProtectedRoute permission="student_dashboard" />}>
        <Route element={<MainLayout />}>
          <Route path={APP_ROUTES.student} element={<Student />} />
        </Route>
      </Route>
      <Route element={<ProtectedRoute permission="admin_dashboard" />}>
        <Route element={<AdminLayout />}>
          <Route path={APP_ROUTES.admin} element={<Admin />} />
        </Route>
      </Route>
      <Route path={APP_ROUTES.notFound} element={<MainLayout><NotFound /></MainLayout>} />
    </Routes>
  );
}
