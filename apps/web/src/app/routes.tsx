import { createBrowserRouter } from "react-router-dom";
import { LandingPageContainer } from "@/features/landing/components/LandingPageContainer";
import { AuthLayout } from "@/features/auth/components/AuthLayout";
import { LoginForm } from "@/features/auth/components/LoginForm";
import { RegisterForm } from "@/features/auth/components/RegisterForm";
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
  // 1. Khám phá & Phiên đọc (Discovery & Reading Sessions)
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

  // 2. Kho Yêu thích (Favorite Library & 4-Entity GraphRAG)
  {
    path: "/library",
    element: <LibraryPage />,
  },

  // 3. Soạn thảo LaTeX (Agentic Overleaf Workspace)
  {
    path: "/writing",
    element: <WritingPage />,
  },
  {
    path: "/writing/:draftId",
    element: <WritingPage />,
  },

  // 4. Tài khoản & Giao diện (Scholar Profile & Account Settings)
  {
    path: "/profile",
    element: <ProfilePage />,
  },
  {
    path: "/settings",
    element: <SettingsPage />,
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
