import { HashRouter, Navigate, Route, Routes } from "react-router-dom";
import { AppLayout } from "@/app/AppLayout";
import { ExperimentPage } from "@/pages/ExperimentPage";
import { HomePage } from "@/pages/HomePage";
import { NotFoundPage } from "@/pages/NotFoundPage";
import { ScenarioPage } from "@/pages/ScenarioPage";

export function AppRouter(): JSX.Element {
  return (
    <HashRouter>
      <Routes>
        <Route element={<AppLayout />} path="/">
          <Route element={<HomePage />} index />
          <Route element={<ExperimentPage />} path="experiments/:experimentId" />
          <Route
            element={<ScenarioPage />}
            path="experiments/:experimentId/scenarios/:scenarioId"
          />
          <Route element={<Navigate replace to="/not-found" />} path="*" />
          <Route element={<NotFoundPage />} path="not-found" />
        </Route>
      </Routes>
    </HashRouter>
  );
}
