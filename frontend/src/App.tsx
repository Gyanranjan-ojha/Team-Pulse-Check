
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./hooks/use-auth";
import { TeamProvider } from "./hooks/use-team";
import { ActivityProvider } from "./hooks/use-activity";

// Layouts
import AppLayout from "./components/layout/AppLayout";
import AuthLayout from "./components/auth/AuthLayout";

// Auth Pages
import Login from "./pages/Auth/Login";
import Register from "./pages/Auth/Register";

// App Pages
import Dashboard from "./pages/Dashboard/Dashboard";
import TeamPage from "./pages/Team/TeamPage";
import ActivityPage from "./pages/Activity/ActivityPage";
import TeamSetup from "./pages/Onboarding/TeamSetup";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <TeamProvider>
        <ActivityProvider>
          <TooltipProvider>
            <Toaster />
            <Sonner />
            <BrowserRouter>
              <Routes>
                {/* Auth Routes */}
                <Route path="/auth" element={<AuthLayout />}>
                  <Route index element={<Navigate to="/auth/login" replace />} />
                  <Route path="login" element={<Login />} />
                  <Route path="register" element={<Register />} />
                </Route>

                {/* Onboarding Routes */}
                <Route path="/onboarding" element={<TeamSetup />} />

                {/* App Routes */}
                <Route path="/" element={<AppLayout />}>
                  <Route index element={<Dashboard />} />
                  <Route path="team" element={<TeamPage />} />
                  <Route path="activity" element={<ActivityPage />} />
                  <Route path="code" element={<ActivityPage />} />
                  <Route path="communication" element={<ActivityPage />} />
                  <Route path="calendar" element={<ActivityPage />} />
                  <Route path="settings" element={<TeamPage />} />
                </Route>

                {/* Catch-all */}
                <Route path="*" element={<NotFound />} />
              </Routes>
            </BrowserRouter>
          </TooltipProvider>
        </ActivityProvider>
      </TeamProvider>
    </AuthProvider>
  </QueryClientProvider>
);

export default App;
