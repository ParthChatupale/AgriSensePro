import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "next-themes";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import ChatBot from "./components/ChatBot";
import InstallPrompt from "./components/InstallPrompt";
import OfflineBanner from "./components/OfflineBanner";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import Advisory from "./pages/Advisory";
import Community from "./pages/Community";
import Report from "./pages/Report";
import Profile from "./pages/Profile";
import UserProfile from "./pages/UserProfile";
import Contact from "./pages/Contact";
import About from "./pages/About";
import Install from "./pages/Install";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <ThemeProvider attribute="class" defaultTheme="light" enableSystem>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <div className="flex flex-col min-h-screen">
            <OfflineBanner />
            <Navbar />
            <main className="flex-1">
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/login" element={<Login />} />
                <Route path="/signup" element={<Signup />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/advisory/:crop" element={<Advisory />} />
                <Route path="/advisory" element={<Advisory />} />
                <Route path="/community" element={<Community />} />
                <Route path="/report" element={<Report />} />
                <Route path="/profile" element={<Profile />} />
                <Route path="/profile/:userId" element={<UserProfile />} />
                <Route path="/contact" element={<Contact />} />
                <Route path="/about" element={<About />} />
                <Route path="/install" element={<Install />} />
                <Route path="*" element={<NotFound />} />
              </Routes>
            </main>
            <Footer />
            <ChatBot />
            <InstallPrompt />
          </div>
        </BrowserRouter>
      </TooltipProvider>
    </ThemeProvider>
  </QueryClientProvider>
);

export default App;
