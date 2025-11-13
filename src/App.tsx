import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import DashboardLayout from "@/layouts/DashboardLayout";
import PriceBotSimple from "@/pages/PriceBotSimple";
import PreordersPage from "@/pages/PreordersPage";
import SalesPageEnhanced from "@/pages/SalesPageEnhanced";
import UnitEconomicsPage from "@/pages/UnitEconomicsPage";
import WhatsAppPage from "@/pages/WhatsAppPage";
import IntegrationPage from "@/pages/IntegrationPage";
import { ThemeProvider } from "./components/theme-provider";
import { Toaster } from "@/components/ui/sonner";



// React Query Client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider defaultTheme="system" storageKey="kaspi-panel-theme">
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard/price-bot" replace />} />
            <Route path="/dashboard" element={<DashboardLayout />}>
              <Route index element={<Navigate to="price-bot" replace />} />
              <Route path="price-bot" element={<PriceBotSimple />} />
              <Route path="sales" element={<SalesPageEnhanced />} />
              <Route path="unit-economics" element={<UnitEconomicsPage />} />
              <Route path="preorders" element={<PreordersPage />} />
              <Route path="whatsapp" element={<WhatsAppPage />} />
              <Route path="integrations" element={<IntegrationPage />} />
            </Route>
            <Route path="*" element={<Navigate to="/dashboard/price-bot" replace />} />
          </Routes>
          <Toaster />
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;