import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LandingPage from "@/pages/LandingPage";
import LoginPage from "@/pages/LoginPage";
import SignupPage from "@/pages/SignupPage";
import DashboardPage from "@/pages/DashboardPage";
import TeamBuilderPage from "@/pages/TeamBuilderPage";
import TeamAnalysisPage from "@/pages/TeamAnalysisPage";
import RecommendationsPage from "@/pages/RecommendationsPage";
import MLBTeamsPage from "@/pages/MLBTeamsPage";
import AppLayout from "@/pages/layouts/AppLayout";
import { ROUTES } from "@/config";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path={ROUTES.LANDING} element={<LandingPage />} />
        <Route path={ROUTES.LOGIN} element={<LoginPage />} />
        <Route path={ROUTES.SIGNUP} element={<SignupPage />} />

        <Route element={<AppLayout />}>
          <Route path={ROUTES.DASHBOARD} element={<DashboardPage />} />
          <Route path={ROUTES.TEAM_BUILDER} element={<TeamBuilderPage />} />
          <Route path={ROUTES.TEAM_ANALYSIS} element={<TeamAnalysisPage />} />
          <Route path={ROUTES.MLB_TEAMS} element={<MLBTeamsPage />} />
        </Route>

        <Route path="*" element={<Navigate to={ROUTES.LANDING} replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
