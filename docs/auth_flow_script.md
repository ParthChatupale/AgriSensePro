# krushiRakshak Signup → Login → Profile Script

Use this script when you want to demonstrate only the authentication and profile setup journey before jumping into the dashboard. Total time ≈ 90 seconds.

---

## 1. Signup (≈35s)

**Screen:** `src/pages/Signup.tsx` (card with 🌿 icon and “Join krushiRakshak”).  
**Narration cues:**
- “We keep onboarding lightweight so a farmer or extension officer can start in under a minute.”
- “They enter name, email, password, phone, and we give a GPS-based ‘Detect location’ option so we can tailor advisories to their farm district.”
- “Fields validate inline, and the CTA clearly says ‘Create your account to get started’.”

**Action:** Fill sample data, click the GPS detect button to show geolocation success toast, submit the form. Mention that the backend hashes the password (bcrypt) and issues a JWT once verification succeeds.

**Key Points to call out:**
- Fast, single-step signup because offline-first users can’t fight a long wizard.
- Auto-location + phone capture ensures we can sync crop advisories and SMS/WhatsApp alerts later.

---

## 2. Login (≈20s)

**Screen:** `src/pages/Login.tsx` (“Welcome Back” card with same gradient).  
**Narration cues:**
- “Returning users just enter email + password. The friendly copy keeps the experience consistent.”
- “On submit we authenticate with FastAPI, issue a fresh JWT, and store it locally so every page (dashboard, advisory, community) knows the user instantly.”

**Action:** Log in with the account you just created and show the redirect to `/dashboard`.

**Key Points:**
- Same UI card as signup → brand consistency.
- JWT session + refresh logic keeps the farmer logged in even when they open the PWA offline.

---

## 3. Profile (≈35s)

**Screen:** `src/pages/Profile.tsx` (Profile Settings card).  
**Narration cues:**
- “After logging in, they can personalize their profile. We fetch their current data using `getCurrentUser()`; if the network is flaky, we gracefully fall back to cached data from localStorage.”
- “They choose a primary crop, enter phone, and can auto-detect geo-coordinates. We lock email/state/district/village so government extension officers can trust the identity.”
- “When they click Save, we call `updateProfile()` so their default crop and location are synced to the advisory engine.”

**Action:** Show the avatar initials, change the primary crop (e.g., Cotton → Wheat), hit Save, wait for success toast.

**Key Points:**
- Auto geolocation button (MapPin icon) writes latitude/longitude directly into the form and shows a toast (“Location detected!”).
- This profile data powers the rest of the app: default crop on dashboard, advisory route (`/advisory/:crop`), and community feed filters.
- Security: unauthenticated visitors get redirected to `/login` thanks to the `isAuthenticated()` guard in the component.

---

### Closing Sentence (use after profile)
“So before we even show any analytics, krushiRakshak already knows who the farmer is, their primary crop, and exact location—meaning every alert and advisory from this point is truly personalized.”


