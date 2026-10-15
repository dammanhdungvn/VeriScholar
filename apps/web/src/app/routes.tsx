import { createBrowserRouter } from "react-router-dom";
import { LandingPageContainer } from "@/features/landing/components/LandingPageContainer";
import { AuthLayout } from "@/features/auth/components/AuthLayout";
import { LoginForm } from "@/features/auth/components/LoginForm";
import { RegisterForm } from "@/features/auth/components/RegisterForm";
import { DashboardPage } from "@/features/dashboard/components/DashboardPage";
import { WritingPage } from "@/features/writing/components/WritingPage";

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
    path: "/writing",
    element: <WritingPage />,
  },
  {
    path: "/writing/:draftId",
    element: <WritingPage />,
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
