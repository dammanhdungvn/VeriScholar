import { createBrowserRouter } from "react-router-dom";
import { LandingPageContainer } from "@/features/landing/components/LandingPageContainer";
import { AuthLayout } from "@/features/auth/components/AuthLayout";
import { LoginForm } from "@/features/auth/components/LoginForm";
import { RegisterForm } from "@/features/auth/components/RegisterForm";
import { DashboardPage } from "@/features/dashboard/components/DashboardPage";
import { PublicShareReader } from "@/features/shares/components/PublicShareReader";
import { DraftingWorkspace } from "@/features/drafts/components/DraftingWorkspace";
import { AdminConsolePage } from "@/features/admin/components/AdminConsolePage";
import { OrganizationsPage } from "@/features/organizations/components/OrganizationsPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <LandingPageContainer />,
  },
  {
    path: "/dashboard",
    element: <DashboardPage />,
  },
  {
    path: "/dashboard/:sessionId",
    element: <DashboardPage />,
  },
  {
    path: "/shares/:token",
    element: <PublicShareReader />,
  },
  {
    path: "/drafts",
    element: <DraftingWorkspace />,
  },
  {
    path: "/drafts/:draftId",
    element: <DraftingWorkspace />,
  },
  {
    path: "/admin",
    element: <AdminConsolePage />,
  },
  {
    path: "/labs",
    element: <OrganizationsPage />,
  },
  {
    element: <AuthLayout />,
    children: [
      {
        path: "/login",
        element: <LoginForm />,
      },
      {
        path: "/register",
        element: <RegisterForm />,
      },
    ],
  },
  {
    path: "*",
    element: <LandingPageContainer />,
  },
]);
