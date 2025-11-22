import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Download, Smartphone, Wifi, CloudOff, CheckCircle } from "lucide-react";
import { toast } from "sonner";

interface BeforeInstallPromptEvent extends Event {
  readonly platforms: string[];
  readonly userChoice: Promise<{
    outcome: "accepted" | "dismissed";
    platform: string;
  }>;
  prompt(): Promise<void>;
}

const Install = () => {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [isInstalled, setIsInstalled] = useState(false);

  useEffect(() => {
    // Check if already installed
    if (window.matchMedia("(display-mode: standalone)").matches) {
      setIsInstalled(true);
      return;
    }

    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e as BeforeInstallPromptEvent);
    };

    window.addEventListener("beforeinstallprompt", handleBeforeInstallPrompt);

    window.addEventListener("appinstalled", () => {
      setIsInstalled(true);
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
    }

    setDeferredPrompt(null);
  };

  const features = [
    {
      icon: Smartphone,
      title: "Works Like a Native App",
      description: "Install on your home screen and access krushiRakshak just like any other app",
    },
    {
      icon: CloudOff,
      title: "Offline Support",
      description: "View cached data and continue working even without internet connection",
    },
    {
      icon: Wifi,
      title: "Auto-Sync",
      description: "Your data syncs automatically when you reconnect to the internet",
    },
    {
      icon: CheckCircle,
      title: "Always Updated",
      description: "Get the latest features automatically without manual updates",
    },
  ];

  return (
    <div className="min-h-screen py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <div className="w-20 h-20 rounded-2xl bg-gradient-hero text-white flex items-center justify-center mx-auto mb-6 shadow-hover">
            <span className="text-4xl">🌿</span>
          </div>
          <h1 className="text-4xl font-heading font-bold text-primary mb-4">
            Install krushiRakshak PWA
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Get the full app experience on your device. Works offline, loads faster, and feels just like a native app.
          </p>
        </div>

        {isInstalled ? (
          <Card className="p-8 text-center shadow-hover bg-gradient-card mb-8">
            <div className="w-16 h-16 rounded-full bg-success/20 flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="h-8 w-8 text-success" />
            </div>
            <h2 className="text-2xl font-heading font-bold mb-2">Already Installed!</h2>
            <p className="text-muted-foreground">
              You're using the installed version of krushiRakshak. Enjoy the full app experience!
            </p>
          </Card>
        ) : (
          <Card className="p-8 text-center shadow-hover bg-gradient-card mb-8">
            <Button
              onClick={handleInstallClick}
              size="lg"
              className="bg-primary hover:bg-primary/90 gap-2 mb-4"
            >
              <Download className="h-5 w-5" />
              Install krushiRakshak
            </Button>
            <p className="text-sm text-muted-foreground">
              Click the button above or use your browser's install option
            </p>
          </Card>
        )}

        {/* Installation Instructions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
          <Card className="p-6 bg-gradient-card">
            <h3 className="font-heading font-bold text-lg mb-4">📱 On Mobile (Android)</h3>
            <ol className="space-y-2 text-sm text-muted-foreground list-decimal list-inside">
              <li>Tap the menu icon (⋮) in your browser</li>
              <li>Select "Add to Home Screen" or "Install app"</li>
              <li>Confirm the installation</li>
              <li>Find krushiRakshak on your home screen</li>
            </ol>
          </Card>

          <Card className="p-6 bg-gradient-card">
            <h3 className="font-heading font-bold text-lg mb-4">📱 On Mobile (iOS)</h3>
            <ol className="space-y-2 text-sm text-muted-foreground list-decimal list-inside">
              <li>Tap the Share button (⎙) in Safari</li>
              <li>Scroll and tap "Add to Home Screen"</li>
              <li>Name the app and tap "Add"</li>
              <li>Find krushiRakshak on your home screen</li>
            </ol>
          </Card>
        </div>

        {/* Features */}
        <h2 className="text-2xl font-heading font-bold text-center mb-8">Why Install?</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {features.map((feature, idx) => (
            <Card key={idx} className="p-6 hover:shadow-hover transition-all bg-gradient-card">
              <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                <feature.icon className="h-6 w-6 text-primary" />
              </div>
              <h3 className="font-heading font-bold mb-2">{feature.title}</h3>
              <p className="text-sm text-muted-foreground">{feature.description}</p>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Install;
