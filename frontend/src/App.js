import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, NavLink, useLocation } from "react-router-dom";
import axios from "axios";
import { Toaster, toast } from "sonner";
import { 
  LayoutDashboard, 
  PlayCircle, 
  Users, 
  TrendingUp, 
  LineChart,
  FileText,
  Download,
  Menu,
  X,
  Database
} from "lucide-react";

// Import pages
import Dashboard from "./pages/Dashboard";
import Pipeline from "./pages/Pipeline";
import CustomerAnalytics from "./pages/CustomerAnalytics";
import Performance from "./pages/Performance";
import Forecasting from "./pages/Forecasting";
import Exports from "./pages/Exports";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

// Navigation items
const navItems = [
  { path: "/", icon: LayoutDashboard, label: "Dashboard" },
  { path: "/pipeline", icon: PlayCircle, label: "Pipeline" },
  { path: "/customers", icon: Users, label: "Customers" },
  { path: "/performance", icon: TrendingUp, label: "Performance" },
  { path: "/forecasting", icon: LineChart, label: "Forecasting" },
  { path: "/exports", icon: Download, label: "Exports" },
];

// Sidebar Component
const Sidebar = ({ isOpen, setIsOpen }) => {
  const location = useLocation();

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}
      
      {/* Sidebar */}
      <aside 
        className={`fixed left-0 top-0 z-50 h-full w-64 bg-[#0F172A] text-white transform transition-transform duration-300 lg:translate-x-0 ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* Logo */}
        <div className="flex items-center gap-3 px-6 py-6 border-b border-white/10">
          <div className="w-10 h-10 rounded-lg bg-[#2563EB] flex items-center justify-center">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <h1 className="font-black text-lg tracking-tight">RetailPulse</h1>
            <p className="text-xs text-white/60">Analytics Platform</p>
          </div>
          <button 
            className="ml-auto lg:hidden"
            onClick={() => setIsOpen(false)}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="px-4 py-6 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              data-testid={`nav-${item.label.toLowerCase()}`}
              className={({ isActive }) => 
                `flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                  isActive 
                    ? "bg-[#2563EB] text-white" 
                    : "text-white/70 hover:bg-white/10 hover:text-white"
                }`
              }
              onClick={() => setIsOpen(false)}
            >
              <item.icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-white/10">
          <div className="text-xs text-white/50 text-center">
            Production-Ready Pipeline
          </div>
        </div>
      </aside>
    </>
  );
};

// Header Component
const Header = ({ setIsOpen }) => {
  const location = useLocation();
  const currentNav = navItems.find(item => item.path === location.pathname);
  
  return (
    <header className="sticky top-0 z-30 bg-white/80 backdrop-blur-md border-b border-border">
      <div className="flex items-center justify-between px-6 py-4">
        <div className="flex items-center gap-4">
          <button 
            className="lg:hidden p-2 hover:bg-muted rounded-lg"
            onClick={() => setIsOpen(true)}
            data-testid="mobile-menu-btn"
          >
            <Menu className="w-5 h-5" />
          </button>
          <div>
            <h2 className="text-xl font-bold tracking-tight text-[#0F172A]">
              {currentNav?.label || "Dashboard"}
            </h2>
            <p className="text-sm text-muted-foreground">
              Retail Analytics Pipeline
            </p>
          </div>
        </div>
      </div>
    </header>
  );
};

// Main App Component
function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-[#F8FAFC]">
        <Toaster position="top-right" richColors />
        
        <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />
        
        <div className="lg:pl-64">
          <Header setIsOpen={setSidebarOpen} />
          
          <main className="p-6 md:p-8">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/pipeline" element={<Pipeline />} />
              <Route path="/customers" element={<CustomerAnalytics />} />
              <Route path="/performance" element={<Performance />} />
              <Route path="/forecasting" element={<Forecasting />} />
              <Route path="/exports" element={<Exports />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
