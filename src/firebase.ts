// firebase.ts
import { initializeApp } from "firebase/app";
import { getMessaging, getToken, onMessage } from "firebase/messaging";

// ---------------------------------------------
// 1️⃣ Your Firebase Web App Configuration
// ---------------------------------------------
const firebaseConfig = {
    apiKey: "AIzaSyAYccvcHaIa0NBSsCYIryVNCU_S05sswws",
    authDomain: "agrisense-56367.firebaseapp.com",
    projectId: "agrisense-56367",
    storageBucket: "agrisense-56367.firebasestorage.app",
    messagingSenderId: "388044731832",
    appId: "1:388044731832:web:cff5a75b6eda7c3b8d8b4d",
    measurementId: "G-C7DTJ2R178"
  };

// ---------------------------------------------
// 2️⃣ Your Real VAPID Public Key
// ---------------------------------------------
const vapidKey =
  "BNUiWFD1eTiDU7bLSAXH93UERIxZL2BFbTbW8g9AeLCLoUl0yQKXoqFzwSbeQvMnOMgYvwcfbBMvYXiJZSGhphI";

// ---------------------------------------------
// 3️⃣ Initialize Firebase App
// ---------------------------------------------
const app = initializeApp(firebaseConfig);
export const messaging = getMessaging(app);

// ---------------------------------------------
// 4️⃣ Request Permission + Token
// ---------------------------------------------
export const requestFcmToken = async () => {
  try {
    const permission = await Notification.requestPermission();
    console.log("Notification Permission:", permission);

    if (permission !== "granted") return null;

    const token = await getToken(messaging, { vapidKey });

    console.log("FCM TOKEN:", token);

    return token;
  } catch (err) {
    console.error("FCM Token Error:", err);
    return null;
  }
};

// ---------------------------------------------
// 5️⃣ Foreground Message Listener (in-app popups)
// ---------------------------------------------
export const listenToMessages = (callback: Function) => {
  onMessage(messaging, (payload) => {
    console.log("Message received in foreground:", payload);
    callback(payload);
  });
};
