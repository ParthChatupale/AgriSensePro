import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "./index.css";
import "./i18n/i18n";

// Register service worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js', { scope: '/' }).catch(() => {
      // Service worker registration handled by vite-plugin-pwa
    });
  });
}

createRoot(document.getElementById("root")!).render(<App />);
