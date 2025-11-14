import { useState, useEffect } from "react";
import { WifiOff, Wifi } from "lucide-react";
import { useTranslation } from "react-i18next";

const OfflineBanner = () => {
  const { t } = useTranslation();
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [showBanner, setShowBanner] = useState(false);

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      setShowBanner(true);
      setTimeout(() => setShowBanner(false), 3000);
    };

    const handleOffline = () => {
      setIsOnline(false);
      setShowBanner(true);
    };

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    // Show initial state if offline
    if (!navigator.onLine) {
      setShowBanner(true);
    }

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  if (!showBanner) return null;

  return (
    <div
      className={`fixed top-16 left-0 right-0 z-50 px-4 py-3 text-center text-sm font-medium animate-slide-up ${
        isOnline
          ? "bg-success text-white"
          : "bg-warning text-warning-foreground"
      }`}
    >
      <div className="flex items-center justify-center gap-2">
        {isOnline ? (
          <>
            <Wifi className="h-4 w-4" />
            <span>{t("offline.online_msg")}</span>
          </>
        ) : (
          <>
            <WifiOff className="h-4 w-4" />
            <span>{t("offline.offline_msg")}</span>
          </>
        )}
      </div>
    </div>
  );
};

export default OfflineBanner;
