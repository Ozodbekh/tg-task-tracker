import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { Layout } from "@/components/Layout";
import { AuthProvider, useAuth } from "@/hooks/AuthContext";
import { FiltersProvider } from "@/hooks/FiltersContext";
import { ChatsPage } from "@/pages/ChatsPage";
import { DashboardPage } from "@/pages/DashboardPage";
import { EmployeeDetailPage } from "@/pages/EmployeeDetailPage";
import { EmployeesPage } from "@/pages/EmployeesPage";
import { LoginPage } from "@/pages/LoginPage";
import { TasksPage } from "@/pages/TasksPage";
import { UnresolvedPage } from "@/pages/UnresolvedPage";

function Shell() {
  const { session, ready } = useAuth();

  if (!ready) {
    return <div className="state">Yuklanmoqda…</div>;
  }

  if (!session) {
    return <LoginPage />;
  }

  return (
    <FiltersProvider>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<DashboardPage />} />
          <Route path="tasks" element={<TasksPage />} />
          <Route path="employees" element={<EmployeesPage />} />
          <Route path="employees/:id" element={<EmployeeDetailPage />} />
          <Route path="chats" element={<ChatsPage />} />
          <Route path="unresolved" element={<UnresolvedPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </FiltersProvider>
  );
}

export function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Shell />
      </AuthProvider>
    </BrowserRouter>
  );
}
