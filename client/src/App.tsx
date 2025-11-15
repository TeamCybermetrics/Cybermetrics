import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LandingPage from "@/pages/LandingPage";
import LoginPage from "@/pages/LoginPage";
import SignupPage from "@/pages/SignupPage";
import TeamBuilderPage from "@/pages/TeamBuilderPage";
import TeamAnalysisPage from "@/pages/TeamAnalysisPage";
import OurAlgorithmPage from "@/pages/OurAlgorithmPage";
import AppLayout from "@/pages/layouts/AppLayout";
import RecommendationsPage from "@/pages/RecommendationsPage";
import { ROUTES } from "@/config";

/**
 * Root application component that configures client-side routing and shared layout.
 *
 * Sets up top-level routes for landing, login, and signup pages, a nested route group
 * wrapped by the shared AppLayout for authenticated pages (dashboard, team builder,
 * team analysis, MLB teams), and a catch-all redirect to the landing route.
 *
 * @returns A JSX element containing the application's router and route configuration.
 */
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path={ROUTES.LANDING} element={<LandingPage />} />
        <Route path={ROUTES.LOGIN} element={<LoginPage />} />
        <Route path={ROUTES.SIGNUP} element={<SignupPage />} />

        <Route element={<AppLayout />}>
          <Route path={ROUTES.TEAM_BUILDER} element={<TeamBuilderPage />} />
          <Route path={ROUTES.TEAM_ANALYSIS} element={<TeamAnalysisPage />} />
          <Route path={ROUTES.RECOMMENDATIONS} element={<RecommendationsPage />} />
          <Route path={ROUTES.OUR_ALGORITHM} element={<OurAlgorithmPage />} />
        </Route>

        <Route path="*" element={<Navigate to={ROUTES.LANDING} replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;