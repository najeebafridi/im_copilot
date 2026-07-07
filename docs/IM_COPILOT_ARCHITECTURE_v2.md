# IM Copilot Architecture v1.0 (Expanded)

> Status: LOCKED
>
> Purpose: This document provides architectural context for a new AI
> coding agent joining the project. It is not user documentation. It
> defines design philosophy, subsystem responsibilities, implementation
> boundaries and locked decisions.

# 1. Vision

IM Copilot is a university academic portal enhanced with an AI
assistant.

The project is intentionally **dashboard-first** rather than chat-first.

Students should immediately see academic information after login.

The assistant supplements the dashboard instead of replacing it.

Guest users are the only users whose primary interface is the assistant.

------------------------------------------------------------------------

# 2. Technology Stack

Backend

-   FastAPI
-   SQLAlchemy
-   SQLite
-   JWT Authentication
-   RBAC
-   ChromaDB
-   LangGraph Router
-   Provider abstraction
-   OpenRouter
-   Mock Provider
-   Python

Frontend

-   React
-   TypeScript
-   Vite
-   TailwindCSS
-   shadcn/ui
-   Axios
-   React Router

------------------------------------------------------------------------

# 3. Backend Modules

Authentication - JWT - Password hashing - RBAC - Student/Admin login -
Guest bypass

Document Pipeline - PDF loading - Cleaning - Chunking - Metadata -
Embeddings - Chroma indexing

SQL Tool - Secure whitelist - Student scoped queries - No arbitrary
SQL - RBAC enforced

RAG - Semantic retrieval - Context building - Prompt construction

LLM Layer - Provider abstraction - OpenRouter - Mock mode - Cache -
Prompt loader

Conversation Engine - RAM storage - UUID conversations - TTL cleanup -
Ownership - Conversation APIs

------------------------------------------------------------------------

# 4. Folder Philosophy

Business logic belongs in services.

API routes remain thin.

Providers expose state.

Pages compose components.

Components remain reusable.

Configuration belongs in config.

Environment variables contain runtime settings.

------------------------------------------------------------------------

# 5. Authentication

Supported Roles

Guest

Student

Administrator

No signup.

No registration.

No forgot password.

No email verification.

No social login.

University creates accounts.

------------------------------------------------------------------------

# 6. Frontend Providers

AuthProvider

Authentication state.

AssistantProvider

Assistant UI only.

ConversationProvider

Conversation data only.

ThemeProvider

Application theme.

Responsibilities must never overlap.

------------------------------------------------------------------------

# 7. Assistant Philosophy

Assistant is NOT the application.

Assistant is a productivity tool.

Dashboard remains visible.

Guest occupies fullscreen assistant.

Student/Admin use floating launcher.

Docking always occurs on the RIGHT.

Assistant Modes

-   CLOSED
-   DOCKED
-   FULLSCREEN

Expanded mode intentionally removed.

------------------------------------------------------------------------

# 8. Conversation Engine

Backend owns

Conversation IDs

Message IDs

Titles

Conversation type

TTL

Cleanup

Ownership

Frontend owns

Rendering

Icons

Animations

Layout

Assistant Mode

Persistence of layout only.

Conversation IDs are UUID4.

Frontend never creates IDs.

------------------------------------------------------------------------

# 9. Conversation APIs

POST /chat/new

GET /chat/list

GET /chat/{id}

POST /chat/{id}/message

DELETE /chat/{id}

GET /chat/status

These endpoints are the only supported conversation interface.

------------------------------------------------------------------------

# 10. Conversation Rules

Most recent first.

No archive.

No pin.

No rename.

No search.

No export.

Delete requires confirmation.

Conversation type is backend data.

Icons are frontend mapping.

------------------------------------------------------------------------

# 11. Assistant Workspace

Assistant Panel

Header

Conversation Sidebar

Workspace

Input

Footer

Floating launcher opens panel.

Close returns to floating launcher.

Fullscreen hides dashboard.

Docked preserves dashboard.

------------------------------------------------------------------------

# 12. Dashboard Philosophy

Student Dashboard contains

Attendance

CGPA

Semester

Quick Actions

Charts

Recent Information

Assistant is opened on demand.

Admin dashboard follows same principle.

------------------------------------------------------------------------

# 13. Guest Experience

Landing

Assistant

Policy questions

No dashboard.

No personal data.

------------------------------------------------------------------------

# 14. Design Language

Professional

Minimal

Institutional

Avoid

Glassmorphism

Marketing pages

Heavy gradients

Flashy animations

------------------------------------------------------------------------

# 15. UI Rules

Conversation sidebar contains

New Conversation

Conversation list

Settings

Profile shown from avatar dropdown only.

No "Logged in as".

No role banners.

------------------------------------------------------------------------

# 16. Storage Rules

Backend stores

Conversation data

Frontend stores

Assistant mode

Panel width

Last selected conversation

Never duplicate backend conversation data.

------------------------------------------------------------------------

# 17. Environment

Backend

CHAT_MEMORY_ENABLED

CHAT_TTL_HOURS

CHAT_MAX_CONVERSATIONS_PER_USER

CHAT_MAX_MESSAGES_PER_CONVERSATION

CHAT_CLEANUP_INTERVAL_MINUTES

CHAT_MAX_TITLE_LENGTH

Frontend

VITE_API_BASE_URL

VITE_ASSISTANT_DEFAULT_MODE

VITE_ENABLE_FULLSCREEN

------------------------------------------------------------------------

# 18. Coding Rules

Never redesign architecture.

Never generate UUIDs in frontend.

Never bypass services.

Never call Axios inside pages/components.

Never hardcode endpoints.

Always use providers.

Always use reusable components.

Prefer composition over duplication.

------------------------------------------------------------------------

# 19. Future Features

Voice

Attachments

Images

Markdown

Streaming

Persistent database history

Faculty role

Registrar role

Notification center

These should plug into existing architecture without redesign.

------------------------------------------------------------------------

# 20. Freeze

This document is the baseline architecture.

Every new AI coding session should:

1.  Read this document.
2.  Inspect repository.
3.  Understand implementation.
4.  Compare with architecture.
5.  Produce implementation plan.
6.  Wait for approval before modifying code.
