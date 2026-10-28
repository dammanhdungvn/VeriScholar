import { createBrowserRouter } from "react-router-dom";
import { LandingPageContainer } from "@/features/landing/components/LandingPageContainer";
import { AuthLayout } from "@/features/auth/components/AuthLayout";
import { LoginForm } from "@/features/auth/components/LoginForm";
import { RegisterForm } from "@/features/auth/components/RegisterForm";
import { AppLayout } from "@/features/dashboard/components/AppLayout";
import { DashboardPage } from "@/features/dashboard/components/DashboardPage";
import { WritingPage } from "@/features/writing/components/WritingPage";
import { ProfilePage } from "@/features/auth/components/ProfilePage";
import { SettingsPage } from "@/features/auth/components/SettingsPage";
import { LibraryPage } from "@/features/library/components/LibraryPage";
import { DiscoveryPage } from "@/features/discovery/components/DiscoveryPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <LandingPageContainer />,
  },
  // Main Application with Persistent Taskbar Layout
  {
    element: <AppLayout />,
    children: [
      {
        path: "/dashboard",
        element: <DashboardPage />,
      },
      {
        path: "/dashboard/:sessionId",
        element: <DashboardPage />,
      },
      {
        path: "/research",
        element: <DashboardPage />,
      },
      {
        path: "/research/:sessionId",
        element: <DashboardPage />,
      },
      {
        path: "/discovery",
        element: <DiscoveryPage />,
      },
      {
        path: "/library",
        element: <LibraryPage />,
      },
      {
        path: "/writing",
        element: <WritingPage />,
      },
      {
        path: "/writing/:draftId",
        element: <WritingPage />,
      },
      {
        path: "/profile",
        element: <ProfilePage />,
      },
      {
        path: "/settings",
        element: <SettingsPage />,
      },
    ],
  },

  // Authentication Flows
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
