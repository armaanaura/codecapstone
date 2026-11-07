# CodeCapstone — Project Context for Codex

## Project purpose
CodeCapstone is a story-driven coding practice platform inspired by LeetCode. Each DSA topic (for example, Graphs) is one continuous narrative. Questions are ordered chapters of that narrative: build a graph, implement BFS, find connected components, and so on. **Each question continues the same topic's story**, has its own difficulty, and is solved/submitted individually.

## Developer preferences / how to work
- Build functionality end to end, **in request-data-flow order**: API route → Pydantic schema → service/business logic → repository/data access → MongoDB/indexes → test.
- Explain **what** and **why** with concise explanations suitable for a developer learning database design for the first time.
- Prefer straightforward Python, FastAPI, Pydantic, and PyMongo. Avoid unnecessary abstractions, frameworks, and complex dependency injection. Simple service/repository classes are fine.
- Implement incrementally. Reuse existing files rather than duplicating code. Do not silently replace functioning code.
- Authentication is **deferred**. Prioritize topics, questions, test cases, progress, submissions, and notes. Creation/editing routes are temporary local-development routes until authorization exists; flag this before public deployment.
- Ask only for missing information that blocks implementation; otherwise select reasonable defaults and explain them.

## Known development environment
- macOS (Apple Silicon), VS Code, Python virtual environment (`venv`).
- Local MongoDB Community Edition is running at `mongodb://127.0.0.1:27017`; database: `codecapstone`.
- MongoDB Compass is used for inspecting collections.
- MongoDB has been tested with `mongosh`; user registration and topic creation via standalone scripts have been exercised in the conversation, although the current project files must be inspected to verify actual implementation state.
- Run Python modules from the directory containing `src/`: `python3 -m tests.test_topic` (not `python3 -m tests.test_topic.py`).

## Intended source layout
```text
codecapstone/
├── src/
│   ├── main.py
│   ├── api/
│   │   ├── router.py
│   │   └── v1/
│   │       ├── auth.py
│   │       ├── users.py
│   │       ├── topics.py
│   │       ├── questions.py
│   │       └── submissions.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── database/
│   │   ├── mongodb.py
│   │   └── indexes.py
│   ├── schemas/
│   │   ├── user.py
│   │   ├── topic.py
│   │   ├── question.py
│   │   └── submission.py
│   ├── repositories/
│   │   ├── user_repository.py
│   │   ├── topic_repository.py
│   │   ├── progress_repository.py
│   │   └── submission_repository.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── topic_service.py
│   │   ├── progress_service.py
│   │   └── submission_service.py
│   └── dependencies/
├── tests/
├── .env
└── .gitignore
```
The tree is a **target layout, not a guarantee that every file exists**. Inspect the repository before editing.

## Architecture and current design decisions
### Users
A `users` document uses MongoDB-generated `_id` (`ObjectId`), unique `username` and `email` indexes, Argon2id `password_hash`, embedded `profile`, small embedded cached `stats`, `role`, `is_active`, `email_verified`, and `created_at`/`updated_at` timestamps. Example:
```json
{
  "username": "armaan",
  "email": "armaan@example.com",
  "password_hash": "<argon2id hash>",
  "profile": {"display_name": "", "bio": "", "avatar_url": null},
  "stats": {
    "total_solved": 0, "easy_solved": 0,
    "medium_solved": 0, "hard_solved": 0, "topics_completed": 0
  },
  "role": "user",
  "is_active": true,
  "email_verified": false
}
```
The real MongoDB document also contains `_id` and timestamps. Never return `password_hash` in a public response. Never store plaintext passwords. `stats` is a derived/cached summary; detailed progress is the source of truth.

### Topics
`topics` stores overall topic metadata and the **story introduction**, but **no topic-level difficulty**. Example fields:
```json
{
  "slug": "graphs",
  "title": "Graph Algorithms",
  "description": "Learn graphs through a continuous story.",
  "story": {
    "title": "The Lost Kingdom",
    "introduction": "Rebuild the kingdom's transportation network."
  },
  "total_questions": 0,
  "is_published": false
}
```
Additional fields: `_id`, `created_at`, `updated_at`. Enforce a unique index on `slug`. `total_questions` is a cached value that should be maintained consistently when questions change.

### Questions
Questions live in a separate `questions` collection. Each references its topic via `topic_id` (`ObjectId`) and has a `sequence_number` that establishes **linear story order**, plus `title`, **question-level** `difficulty` (`easy` / `medium` / `hard`), story narrative/objective, problem statement/constraints, **2–3 embedded public `sample_test_cases`**, evaluation configuration (`mode`, time/memory limits), `is_published`, and timestamps.
- Create a unique compound index on `(topic_id, sequence_number)`.
- Retrieve topic questions sorted by `sequence_number` ascending.
- The story continues across questions, but coding submissions may be evaluated independently unless requirements change.
- Consider question/content versioning before allowing edits to published questions affecting existing submissions or progress.

### Hidden test cases
Store hidden evaluation tests **separately** in `test_cases`, indexed by `question_id`. Do **not** include hidden tests in user-facing question API responses. For very large tests, use object storage with references in MongoDB. A fixed expected output is insufficient for questions with multiple valid answers; allow for a custom validation mode.

### Other planned collections
- `question_progress`: source of truth for each user's solved state and first solve date; unique `(user_id, question_id)` to prevent duplicates.
- `topic_progress`: per-user topic/chapter progress; avoid duplicating extensive solved-question arrays unnecessarily.
- `submissions`: append-only submission records (code, language, verdict, execution metadata, timestamps); many submissions per question/user.
- `question_workspace`: user-specific notes and saved draft code for each question.
- `auth_sessions`: refresh-token/session revocation management **later**.

## Data integrity / concurrency
- `users.username`, `users.email`, and `topics.slug` must be protected by **database unique indexes**, not only pre-insert lookups; catch `DuplicateKeyError` to handle races.
- Count a solved question only upon the **first successful transition** to solved. Concurrent accepted submissions must not double-count. Use an atomic conditional write / unique upsert for the source-of-truth progress record. If both progress and cached stats must change strictly together, use a MongoDB transaction or a deliberate reconciliation strategy.
- Avoid embedding unbounded arrays (such as all submissions) in a MongoDB document.

## Layer responsibilities
- API (`src/api/v1/*.py`): HTTP validation/response and status codes; no direct database queries.
- Pydantic schemas (`src/schemas/*.py`): request/response and stored-data validation; keep private fields out of public responses.
- Services (`src/services/*.py`): business rules and orchestration.
- Repositories (`src/repositories/*.py`): MongoDB operations.
- Database (`src/database/*.py`): shared asynchronous client, collections, and index setup.
- Use `pymongo.AsyncMongoClient` with async methods and a shared client. Prefer simple manual repository/service wiring when appropriate; do not instantiate a new MongoDB client per request.
- Use snake_case field names consistently between Python and MongoDB. Handle `ObjectId` ↔ string conversion at the persistence/API boundary.

## Topic creation HTTP flow (actively being built)
Intended endpoint: `POST /api/v1/topics/` returning `201 Created`; duplicate slug returns `409 Conflict`.
```text
main.py -> api/router.py -> api/v1/topics.py
    -> Pydantic TopicCreate -> TopicService -> TopicRepository
    -> MongoDB codecapstone.topics
```
Expected request:
```json
{
  "slug": "graphs",
  "title": "Graph Algorithms",
  "description": "Learn graphs through a continuous storyline.",
  "story": {
    "title": "The Lost Kingdom",
    "introduction": "You must rebuild the kingdom's transportation network."
  }
}
```
Earlier designs already included `TopicCreate`, `TopicInDB`, `TopicPublic`, `TopicRepository`, `TopicService`, `create_indexes`, and `src/main.py`. **Inspect actual files and resolve discrepancies** rather than assuming every snippet was applied. In particular, the repository constructor expects a MongoDB collection, not the topic request data. Previous iterations used either manual wiring or FastAPI `Depends`; current preference is simple Python and manual wiring where reasonable.

## Local run / tests
```bash
# From codecapstone/ containing src/
source venv/bin/activate
uvicorn src.main:app --reload
# Visit http://127.0.0.1:8000/docs
python3 -m tests.test_topic
mongosh
# In mongosh: use codecapstone; db.topics.find().pretty()
```
A historical `/health` endpoint returned `{"status": "healthy"}`; this checks the HTTP app, not necessarily live DB reachability for each request.

## Safety and operational notes
- MongoDB currently reports that **access control is disabled**. Keep it bound to `127.0.0.1` for local development; never expose it publicly without authentication/network controls.
- Keep credentials and `.env` out of Git; maintain `.env.example` with placeholders.
- Creation endpoints need admin authorization before production deployment.
- Run user code only in a properly isolated execution environment with enforced CPU/time/memory/network limits; never execute arbitrary submitted code directly in the FastAPI server process.
- Password hashing with Argon2id is CPU/memory intensive. In async request handlers, offload it to a thread so it does not block the event loop.

## Immediate next work
1. Inspect current `src/main.py`, `src/api/router.py`, and topic modules.
2. Complete and locally test the **end-to-end topic creation endpoint** in request-flow order, preserving existing work.
3. Implement ordered questions with embedded public samples.
4. Implement separate hidden test-case storage and evaluation metadata.
5. Then progress, submissions, and question notes/drafts. Authentication later.

This document summarizes the project decisions from a prior ChatGPT design conversation. The **repository source code is authoritative** if anything here differs from its current implementation.
