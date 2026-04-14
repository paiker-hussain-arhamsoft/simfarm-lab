import { Switch, Route, Router as WouterRouter } from "wouter";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
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
import NotFound from "@/pages/not-found";

const queryClient = new QueryClient();

function Router() {
  return (
    <Switch>
      <Route path="/" component={ComplianceGateway} />
      <Route path="/access" component={AccessGranted} />
      <Route path="/tool" component={StrategicBrain} />
      <Route path="/tier2" component={IntelligenceCrew} />
      <Route path="/media-crew" component={MediaCrew} />
      <Route path="/video-stack" component={VideoStack} />
      <Route path="/cyber-crew" component={CyberCrew} />
      <Route path="/persona-orchestration" component={PersonaOrchestration} />
      <Route path="/sim-farm" component={SimFarm} />
      <Route path="/proxy-rotation" component={ProxyRotation} />
      <Route path="/admin" component={AdminPanel} />
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
