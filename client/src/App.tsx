import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LandingPage from "@/pages/LandingPage";
import LoginPage from "@/pages/LoginPage";
import SignupPage from "@/pages/SignupPage";
import TeamBuilderPage from "@/pages/TeamBuilderPage";
import OurAlgorithmPage from "@/pages/OurAlgorithmPage";
import AppLayout from "@/pages/layouts/AppLayout";
import RecommendationsPage from "@/pages/RecommendationsPage";
import { ROUTES } from "@/config";

/**
 * Configure client-side routing and render the application's root router with a shared layout for authenticated pages.
 *
 * @returns The root JSX element that renders BrowserRouter and the application's route configuration
 */
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path={ROUTES.LANDING} element={<LandingPage />} />
        <Route path={ROUTES.LOGIN} element={<LoginPage />} />
        <Route path={ROUTES.SIGNUP} element={<SignupPage />} />

        <Route element={<AppLayout />}>
          <Route path={ROUTES.LINEUP_CONSTRUCTOR} element={<TeamBuilderPage />} />
          <Route path={ROUTES.ROSTER_CONSTRUCTOR} element={<RecommendationsPage />} />
          <Route path={ROUTES.OUR_ALGORITHM} element={<OurAlgorithmPage />} />
        </Route>

        <Route path="*" element={<Navigate to={ROUTES.LANDING} replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;