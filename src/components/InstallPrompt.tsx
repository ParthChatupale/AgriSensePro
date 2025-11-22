import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { X, Download } from "lucide-react";
import { toast } from "sonner";

interface BeforeInstallPromptEvent extends Event {
  readonly platforms: string[];
  readonly userChoice: Promise<{
    outcome: "accepted" | "dismissed";
    platform: string;
  }>;
  prompt(): Promise<void>;
}

const InstallPrompt = () => {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [showPrompt, setShowPrompt] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);

  useEffect(() => {
    // Check if already installed
    if (window.matchMedia("(display-mode: standalone)").matches) {
      setIsInstalled(true);
      return;
    }

    // Listen for install prompt event
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e as BeforeInstallPromptEvent);
      
      // Show prompt after a delay (don't be intrusive)
      setTimeout(() => {
        const hasDeclined = localStorage.getItem("pwa-install-declined");
        if (!hasDeclined) {
          setShowPrompt(true);
        }
      }, 3000);
    };

    window.addEventListener("beforeinstallprompt", handleBeforeInstallPrompt);

    // Listen for successful installation
    window.addEventListener("appinstalled", () => {
      setIsInstalled(true);
      setShowPrompt(false);
      toast.success("krushiRakshak installed successfully! 🌿");
    });

    return () => {
      window.removeEventListener("beforeinstallprompt", handleBeforeInstallPrompt);
    };
  }, []);

  const handleInstallClick = async () => {
    if (!deferredPrompt) {
      toast.info("To install, use your browser's 'Add to Home Screen' option");
      return;
    }

    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;

    if (outcome === "accepted") {
      toast.success("Installing krushiRakshak...");
    } else {
      localStorage.setItem("pwa-install-declined", "true");
    }

    setDeferredPrompt(null);
    setShowPrompt(false);
  };

  const handleDismiss = () => {
    setShowPrompt(false);
    localStorage.setItem("pwa-install-declined", "true");
  };

  if (isInstalled || !showPrompt) {
    return null;
  }

  return (
    <Card className="fixed bottom-6 left-6 right-6 md:left-auto md:right-6 md:w-96 p-4 shadow-hover z-40 bg-gradient-card border-2 border-primary/20 animate-slide-up">
      <button
        onClick={handleDismiss}
        className="absolute top-2 right-2 text-muted-foreground hover:text-foreground transition-colors"
      >
        <X className="h-4 w-4" />
      </button>

      <div className="flex items-start gap-4">
        <div className="w-12 h-12 rounded-xl bg-gradient-hero flex items-center justify-center flex-shrink-0">
          <span className="text-2xl">🌿</span>
        </div>
        <div className="flex-1">
          <h3 className="font-heading font-bold text-lg mb-1">Install krushiRakshak</h3>
          <p className="text-sm text-muted-foreground mb-3">
            Get quick access and work offline. Install our app on your device!
          </p>
          <div className="flex gap-2">
            <Button onClick={handleInstallClick} size="sm" className="bg-primary hover:bg-primary/90 gap-2">
              <Download className="h-4 w-4" />
              Install App
            </Button>
            <Button onClick={handleDismiss} size="sm" variant="ghost">
              Not Now
            </Button>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default InstallPrompt;
