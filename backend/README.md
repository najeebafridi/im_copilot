# IM Copilot Backend

Phase 4.5 of the IM Copilot project refines the reusable LLM service layer on top of the earlier backend phases.

## Requirements

- Python 3.13.6

## Setup

1. Create and activate a virtual environment.
2. Install dependencies.
3. Copy `.env.example` to `.env` if you want to override defaults.

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

## Database

Initialize the SQLite schema:

```bash
cd backend
python init_db.py
```

Seed the demo data:

```bash
cd backend
python seed.py
```

## Documents Folder

Place your source documents here:

```text
backend/documents/
```

Supported file types:

- `.pdf`
- `.docx`
- `.txt`
- `.md`

The ingestion pipeline writes debug outputs here:

```text
backend/processed/
```

The local Chroma database is stored here:

```text
backend/data/chroma/
```

## Phase 3 Manual Workflow

1. Copy your documents into `backend/documents/`.
2. Start the API:

```bash
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

3. Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

4. Run `POST /api/v1/documents/ingest`.
5. Watch the terminal for progress prints such as:

```text
[INGEST] Found ...
[INGEST] Processing ...
[INGEST] Completed ...
```

6. Check the generated debug files in `backend/processed/`.
7. Run `GET /api/v1/rag/search?query=attendance requirement&k=5`.

## Phase 4 Manual Workflow

1. Put the LLM configuration into `.env`.
2. Keep `MOCK_LLM=True` for safe local testing, or set it to `False` only when real provider credentials are ready.
3. Start the API:

```bash
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

4. Open Swagger:

```text
http://127.0.0.1:8000/docs
```

5. Test the endpoint:

```text
POST /api/v1/llm/test
```

6. In the request body, send:

```json
{
  "message": "Hello"
}
```

7. When `MOCK_LLM=True`, expect a deterministic mock response and terminal prints like:

```text
[LLM] request started ...
[LLM] request completed ...
```

## Phase 4.5 Manual Workflow

1. Set the LLM provider in `.env`.
2. Use `MOCK_LLM=True` for local testing, or set `MOCK_LLM=False` with valid provider credentials.
3. Optional cache settings:

```text
ENABLE_CACHE=True
CACHE_SIZE=100
```

4. Optional provider selection:

```text
LLM_PROVIDER=mock
LLM_PROVIDER=openai
LLM_PROVIDER=openrouter
LLM_PROVIDER=grok
```

5. Start the API:

```bash
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

6. Open Swagger:

```text
http://127.0.0.1:8000/docs
```

7. Call:

```text
POST /api/v1/llm/test
```

8. Send this body:

```json
{
  "message": "Hello"
}
```

9. The first identical request should hit the provider.
10. Repeating the same request should use the cache when enabled.

## Phase 5 Manual Workflow

1. Make sure your documents have already been ingested in Phase 3.
2. Start the backend:

```bash
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

3. Open Swagger:

```text
http://127.0.0.1:8000/docs
```

4. Test retrieval first if you want to inspect chunks:

```text
GET /api/v1/rag/search?query=attendance requirement&k=3
```

5. Test the new grounded chat endpoint:

```text
POST /api/v1/copilot/chat
```

6. Use this request body:

```json
{
  "conversation_id": "demo-1",
  "message": "What is the attendance requirement?"
}
```

7. Expected behavior:

```text
- Relevant document chunks are retrieved
- A structured prompt is built from the chunks
- The configured LLM is called
- The response is grounded in the supplied context
- Source information is returned
```

8. Suggested manual questions:

```text
What is the attendance requirement?
What documents are required for medical leave?
What is the grading policy?
```

## Phase 6 Manual Workflow

1. Start the backend:

```bash
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

2. Log in with a seeded student account:

```text
student_id: DS001
password: password123
```

3. In Swagger, use `POST /api/v1/auth/login`.
4. Click **Authorize** in Swagger and paste the bearer token.
5. Test the academic endpoint:

```text
POST /api/v1/academic/chat
```

6. Example request body:

```json
{
  "conversation_id": "demo-1",
  "message": "What is my CGPA?"
}
```

7. Suggested questions:

```text
What is my name?
What is my semester?
What is my program?
What is my CGPA?
What is my attendance?
What is my attendance in DS301?
What is my highest attendance?
What is my lowest attendance?
What are my enrolled courses?
What are my grades?
What is my timetable?
```

8. Expected behavior:

```text
- Only the authenticated student's records are returned
- Unsupported questions return a clean error
- Missing records return a clean error
- The LLM explains only the returned database data
- Sources include type=database and the table name
```

9. RBAC check:

```text
- Try the endpoint without a token: it should fail with 401
- Try the endpoint with a valid token: it should succeed
- The returned data should never belong to another student
```

## Phase 7A Manual Workflow

1. Make sure the backend is started:

```bash
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

2. Open Swagger:

```text
http://127.0.0.1:8000/docs
```

3. Test the unified router endpoint:

```text
POST /api/v1/copilot/chat
```

4. Use these sample messages:

```text
Hi
What is my CGPA?
What is attendance policy?
Who won the FIFA World Cup?
```

5. Expected routing:

```text
Hi -> Greeting Node
What is my CGPA? -> Academic SQL Tool
What is attendance policy? -> RAG Tool
Who won the FIFA World Cup? -> Fallback Node
```

6. For academic questions like `What is my CGPA?`, click **Authorize** in Swagger and paste a valid bearer token first.
7. To enable router debug mode, set this in `.env`:

```text
ROUTER_DEBUG=True
```

8. Restart the backend after changing `.env`.
9. When debug mode is on, the response includes a `debug` block with normalized query, matched keywords, scores, selected intent, selected node, and routing time.
10. When debug mode is off, the `debug` block is omitted completely.
11. Check the terminal for router logs showing:

```text
[ROUTER] question=...
[ACADEMIC] ...
[COPILOT] ...
```

## Run

```bash
cd backend
uvicorn app.main:app --reload
```

## Health Check

Visit:

```bash
GET http://127.0.0.1:8000/api/v1/health
```

Expected response:

```json
{
  "status": "ok",
  "project": "IM Copilot"
}
```

## Test

```bash
cd backend
pytest
```
