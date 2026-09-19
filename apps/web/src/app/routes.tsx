import { createBrowserRouter } from "react-router-dom";
import { LandingPageContainer } from "@/features/landing/components/LandingPageContainer";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <LandingPageContainer />,
  },
  {
    path: "*",
    element: <LandingPageContainer />,
  },
]);
