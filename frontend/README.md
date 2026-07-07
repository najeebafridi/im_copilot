# IM Copilot Frontend

Frontend Phase F1 creates the project foundation only. It does not implement business logic, backend calls, authentication, chat, or dashboard features.

## Tech Stack

- React 19
- Vite
- TypeScript
- React Router DOM
- Tailwind CSS
- shadcn/ui
- Recharts
- Lucide React
- Axios
- Sonner
- react-markdown

## Setup

1. Go to the frontend folder:

```powershell
cd frontend
```

2. Create a virtual environment is not needed here because this is a Node frontend project.
3. Install dependencies:

```powershell
npm install
```

4. Copy `.env.example` to `.env`:

```powershell
copy .env.example .env
```

5. Start the development server:

```powershell
npm run dev
```

6. Open the app in the browser:

```text
http://127.0.0.1:5173
```

## Manual Testing Guide

1. Confirm the app starts without build errors.
2. Open each route:
   - `/`
   - `/login`
   - `/student`
   - `/guest`
   - `/admin`
3. Confirm the 404 page appears for an unknown route.
4. Confirm the Tailwind classes are applied to the layout and placeholder pages.
5. Confirm React Router switches between pages.
6. Confirm the main layout renders header, sidebar, main area, and footer placeholders.
7. Confirm the admin layout renders header, sidebar, and content placeholders.
8. Confirm the axios client compiles and uses the configured base URL and timeout.
9. Confirm environment variables are loaded through `src/config/env.ts`.
10. Confirm the folder structure matches the phase specification.

## Phase F2A Manual Testing Guide

1. Start the frontend:

```powershell
cd frontend
npm run dev
```

2. Open:

```text
http://127.0.0.1:5173
```

3. Confirm the landing page shows three links:
   - Continue as Guest
   - Continue as Student
   - Continue as Administrator
4. Click **Continue as Guest** and confirm the `/guest` page opens immediately.
5. Go back to `/` and click **Continue as Student**.
6. Confirm the student login page opens with:
   - Student ID field
   - Password field
   - Stay Logged In checkbox
   - Login button
7. Log in with:

```text
Student ID: DS001
Password: password123
```

8. Try both storage modes:
   - Check **Stay Logged In** for `localStorage`
   - Uncheck it for `sessionStorage`
9. After login, confirm you are redirected to `/student`.
10. Refresh the page and confirm the session is restored automatically.
11. Click **Logout** and confirm you return to `/`.
12. Visit `/student` while logged out and confirm you are redirected to `/`.
13. Visit `/admin/login` and confirm the administrator login page opens.
14. Try invalid credentials and confirm a simple text error appears.
15. Inspect browser storage:
   - `localStorage` should contain the token/user when Stay Logged In is checked
   - `sessionStorage` should contain the token/user when it is unchecked
16. Confirm the Authorization header is attached by checking backend requests in the browser network tab after login.
17. Confirm the loading screen appears briefly on refresh:

```text
Loading IM Copilot...
```

## Notes

- The backend is intentionally untouched.
- The frontend is only a foundation for later phases.
