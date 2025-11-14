import { useState, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Menu, X, Bell, Globe, ChevronDown, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useTheme } from "next-themes";
import { isAuthenticated, logoutUser, getUser } from "@/services/api";
import { useTranslation } from "react-i18next";
import i18n from "@/i18n/i18n";

const Navbar = () => {
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const [authenticated, setAuthenticated] = useState(false);
  const [user, setUser] = useState<any>(null);
  const location = useLocation();
  const navigate = useNavigate();
  const { theme, setTheme } = useTheme();

  useEffect(() => {
    // Check authentication status
    const checkAuth = () => {
      const isAuth = isAuthenticated();
      setAuthenticated(isAuth);
      if (isAuth) {
        setUser(getUser());
      } else {
        setUser(null);
      }
    };

    checkAuth();
    // Check on route changes (less frequent polling)
    const interval = setInterval(checkAuth, 2000);
    return () => clearInterval(interval);
  }, [location]);

  const handleLogout = () => {
    logoutUser();
    setAuthenticated(false);
    setUser(null);
    navigate("/login");
  };

  const navLinks = [
    { name: t("nav.home"), path: "/", key: "home" },
    { name: t("nav.dashboard"), path: "/dashboard", key: "dashboard" },
    { name: t("nav.advisory"), path: "/advisory", key: "advisory" },
    { name: t("nav.community"), path: "/community", key: "community" },
    { name: t("nav.report"), path: "/report", key: "report" },
    { name: t("nav.contact"), path: "/contact", key: "contact" },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="sticky top-0 z-50 w-full bg-card/95 backdrop-blur supports-[backdrop-filter]:bg-card/80 border-b border-border shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2 flex-shrink-0">
            <div className="w-8 h-8 bg-gradient-hero rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">🌿</span>
            </div>
            <div className="hidden sm:block">
              <h1 className="font-heading font-bold text-lg text-primary">AgriSense</h1>
              <p className="text-xs text-muted-foreground leading-none">{t("navbar.tagline")}</p>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden lg:flex items-center space-x-1">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive(link.path)
                    ? "bg-primary text-primary-foreground"
                    : "text-foreground hover:bg-muted"
                }`}
              >
                {link.name}
              </Link>
            ))}
          </div>

          {/* Right Side Icons */}
          <div className="flex items-center space-x-2">
            {/* Language Toggle */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="hidden md:flex">
                  <Globe className="h-5 w-5" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="bg-popover">
                <DropdownMenuItem onClick={() => i18n.changeLanguage("en")}>
                  English
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => i18n.changeLanguage("mr")}>
                  मराठी (Marathi)
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            {/* Dark Mode Toggle */}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              className="hidden md:flex"
            >
              {theme === "dark" ? "🌙" : "☀️"}
            </Button>

            {/* Notifications */}
            <Button variant="ghost" size="icon" className="hidden md:flex relative">
              <Bell className="h-5 w-5" />
              <span className="absolute top-1 right-1 h-2 w-2 bg-destructive rounded-full"></span>
            </Button>

            {/* Profile Dropdown - Only show when authenticated */}
            {authenticated ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="hidden md:flex">
                  <User className="h-5 w-5" />
                  <ChevronDown className="h-3 w-3 ml-1" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="bg-popover">
                  {user && (
                    <div className="px-2 py-1.5 text-sm font-semibold border-b">
                      {user.name}
                    </div>
                  )}
                <DropdownMenuItem asChild>
                  <Link to="/profile">{t("navbar.profile")}</Link>
                </DropdownMenuItem>
                <DropdownMenuItem>{t("navbar.settings")}</DropdownMenuItem>
                  <DropdownMenuItem onClick={handleLogout}>
                    {t("auth.logout")}
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
            ) : (
              <Button variant="ghost" asChild className="hidden md:flex">
                <Link to="/login">{t("auth.login")}</Link>
              </Button>
            )}

            {/* Mobile Menu Button */}
            <Button
              variant="ghost"
              size="icon"
              className="lg:hidden"
              onClick={() => setIsOpen(!isOpen)}
            >
              {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </Button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {isOpen && (
        <div className="lg:hidden bg-card border-t border-border">
          <div className="px-2 pt-2 pb-3 space-y-1">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                onClick={() => setIsOpen(false)}
                className={`block px-3 py-2 rounded-md text-base font-medium ${
                  isActive(link.path)
                    ? "bg-primary text-primary-foreground"
                    : "text-foreground hover:bg-muted"
                }`}
              >
                {link.name}
              </Link>
            ))}
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
