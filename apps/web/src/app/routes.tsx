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
import { ComparisonMatrixPage } from "@/features/library/components/ComparisonMatrixPage";
import { NotesPage } from "@/features/notes/components/NotesPage";
import { DiscoveryPage } from "@/features/discovery/components/DiscoveryPage";
import { ProjectsPage } from "@/features/dashboard/components/ProjectsPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <LandingPageContainer />,
  },
  // Module 1: Deep Reading & Research Socratic Copilot
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

  // Module 4: Personal Paper Library & Folders
  {
    path: "/library",
    element: <LibraryPage />,
  },
  // Module 4: Scalable 100+ Paper Comparison Matrix
  {
    path: "/library/matrix",
    element: <ComparisonMatrixPage />,
  },
  {
    path: "/matrix",
    element: <ComparisonMatrixPage />,
  },

  // Module 1 & 4: Smart Notes & AI Knowledge Synthesis
  {
    path: "/notes",
    element: <NotesPage />,
  },

  // Module 3: Academic Discovery & Citation Network
  {
    path: "/discovery",
    element: <DiscoveryPage />,
  },
  {
    path: "/citations",
    element: <DiscoveryPage />,
  },

  // Research Projects & Collections
  {
    path: "/projects",
    element: <ProjectsPage />,
  },

  // Module 2: Academic Writing & SAFE Verification
  {
    path: "/writing",
    element: <WritingPage />,
  },
  {
    path: "/writing/:draftId",
    element: <WritingPage />,
  },

  // Module 5: Scholar Profile & Account Settings
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
