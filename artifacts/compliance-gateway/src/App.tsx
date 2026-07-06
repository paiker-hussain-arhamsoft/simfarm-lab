import { Switch, Route, Router as WouterRouter, useLocation } from "wouter";
import { useEffect } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import Login from "@/pages/Login";
import ComplianceGateway from "@/pages/ComplianceGateway";
import AccessGranted from "@/pages/AccessGranted";
import AdminPanel from "@/pages/AdminPanel";
import StrategicBrain from "@/pages/StrategicBrain";
import IntelligenceCrew from "@/pages/IntelligenceCrew";
import MediaCrew from "@/pages/MediaCrew";
import VideoStack from "@/pages/VideoStack";
import CyberCrew from "@/pages/CyberCrew";
import PersonaOrchestration from "@/pages/PersonaOrchestration";
import SimFarm from "@/pages/SimFarm";
import ProxyRotation from "@/pages/ProxyRotation";
import IvrSystems from "@/pages/IvrSystems";
import ContentDistribution from "@/pages/ContentDistribution";
import StealthDetection from "@/pages/StealthDetection";
import MemoryPersistence from "@/pages/MemoryPersistence";
import PrivacyPolicy from "@/pages/PrivacyPolicy";
import UserAgreement from "@/pages/UserAgreement";
import Documentation from "@/pages/Documentation";
import NotFound from "@/pages/not-found";

const queryClient = new QueryClient();

function checkAuth(): boolean {
  return (
    !!sessionStorage.getItem("oeads_auth_token") &&
    !!localStorage.getItem("oeads_portal_key")
  );
}

function AuthGuard({ children }: { children: React.ReactNode }) {
  const [, navigate] = useLocation();

  useEffect(() => {
    if (!checkAuth()) {
      navigate("/login");
    }
  }, [navigate]);

  if (!checkAuth()) return null;
  return <>{children}</>;
}

function Router() {
  return (
    <Switch>
      <Route path="/login" component={Login} />
      <Route path="/privacy-policy" component={PrivacyPolicy} />
      <Route path="/user-agreement" component={UserAgreement} />
      <Route path="/documentation" component={Documentation} />

      <Route path="/">
        {() => <AuthGuard><ComplianceGateway /></AuthGuard>}
      </Route>
      <Route path="/access">
        {() => <AuthGuard><AccessGranted /></AuthGuard>}
      </Route>
      <Route path="/tool">
        {() => <AuthGuard><StrategicBrain /></AuthGuard>}
      </Route>
      <Route path="/tier2">
        {() => <AuthGuard><IntelligenceCrew /></AuthGuard>}
      </Route>
      <Route path="/media-crew">
        {() => <AuthGuard><MediaCrew /></AuthGuard>}
      </Route>
      <Route path="/video-stack">
        {() => <AuthGuard><VideoStack /></AuthGuard>}
      </Route>
      <Route path="/cyber-crew">
        {() => <AuthGuard><CyberCrew /></AuthGuard>}
      </Route>
      <Route path="/persona-orchestration">
        {() => <AuthGuard><PersonaOrchestration /></AuthGuard>}
      </Route>
      <Route path="/sim-farm">
        {() => <AuthGuard><SimFarm /></AuthGuard>}
      </Route>
      <Route path="/proxy-rotation">
        {() => <AuthGuard><ProxyRotation /></AuthGuard>}
      </Route>
      <Route path="/ivr-systems">
        {() => <AuthGuard><IvrSystems /></AuthGuard>}
      </Route>
      <Route path="/content-distribution">
        {() => <AuthGuard><ContentDistribution /></AuthGuard>}
      </Route>
      <Route path="/stealth-detection">
        {() => <AuthGuard><StealthDetection /></AuthGuard>}
      </Route>
      <Route path="/memory-persistence">
        {() => <AuthGuard><MemoryPersistence /></AuthGuard>}
      </Route>
      <Route path="/admin">
        {() => <AuthGuard><AdminPanel /></AuthGuard>}
      </Route>
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, "")}>
          <Router />
        </WouterRouter>
        <Toaster />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
