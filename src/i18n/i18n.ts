// src/i18n/i18n.ts
import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";

import en from "./locales/en.json";
import mr from "./locales/mr.json";

i18n
  .use(LanguageDetector) // detects from navigator / localStorage
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      mr: { translation: mr },
    },
    fallbackLng: "en",
    debug: false, // set true for development troubleshooting
    interpolation: {
      escapeValue: false, // react already escapes
    },
    detection: {
      // order and keys for language detection
      order: ["localStorage", "navigator", "htmlTag"],
      caches: ["localStorage"],
      lookupLocalStorage: "i18nextLng",
    },
    react: {
      useSuspense: false,
    },
  });

// Global helper for language switching
if (typeof window !== "undefined") {
  (window as any).setLanguage = (lang: "en" | "mr") => {
    i18n.changeLanguage(lang);
  };
  (window as any).switchLang = (lang: "en" | "mr") => {
    i18n.changeLanguage(lang);
  };
}

export default i18n;
