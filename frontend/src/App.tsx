import { Navigate, Route, Routes } from "react-router-dom";

import { ComingSoon } from "./components/ComingSoon";
import { Layout } from "./components/Layout";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { CampaignDetail } from "./pages/Campaigns/CampaignDetail";
import { Campaigns } from "./pages/Campaigns/Campaigns";
import { ContentGenerator } from "./pages/ContentGenerator/ContentGenerator";
import { Dashboard } from "./pages/Dashboard/Dashboard";
import { Login } from "./pages/Login/Login";
import { Register } from "./pages/Login/Register";
import { BrandSettings } from "./pages/Settings/BrandSettings";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/brand-settings" element={<BrandSettings />} />

        <Route path="/campaigns" element={<Campaigns />} />
        <Route path="/campaigns/:campaignId" element={<CampaignDetail />} />
        <Route path="/content-generator" element={<ContentGenerator />} />
        <Route path="/calendar" element={<ComingSoon title="Content Calendar" phase="Phase 4" />} />
        <Route path="/posts" element={<ComingSoon title="Posts" phase="Phase 4" />} />
        <Route path="/analytics" element={<ComingSoon title="Analytics" phase="Phase 5" />} />
        <Route path="/insights" element={<ComingSoon title="AI Insights" phase="Phase 6" />} />
        <Route
          path="/recommendations"
          element={<ComingSoon title="Recommendations" phase="Phase 6" />}
        />
        <Route
          path="/social-accounts"
          element={<ComingSoon title="Social Accounts" phase="Phase 3" />}
        />
        <Route path="/team" element={<ComingSoon title="Team & Roles" phase="Phase 2" />} />
        <Route path="/settings" element={<ComingSoon title="Settings" phase="Phase 2" />} />

        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Route>

      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
