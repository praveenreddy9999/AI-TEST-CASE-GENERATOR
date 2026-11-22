# AI Test Case Generator Agent

A local-first AI web application that converts plain-English software requirements into structured manual test cases. It generates positive, negative, and edge-case scenarios, assigns priorities, and lets users review, edit, delete, save, reload, and export test cases as CSV.

## Features

- Requirement input in simple English.
- Agent workflow: analyze requirement → select scenarios → generate → validate.
- Positive, Negative, and Edge case test scenarios.
- Each test case includes ID, title, preconditions, steps, test data, expected result, and priority.
- Supported priorities: High, Medium, Low.
- Human-editable results and individual case deletion.
- SQLite history that persists after application restart.
- CSV export using Pandas.
- Empty-input, invalid-response, and Ollama connection error handling.
- Local LLM usage through Ollama; no paid API key required.

## Technology stack

- Python — application logic and validation
- Streamlit — web interface
- Ollama + local LLM — requirement understanding and test generation
- LangChain — local chat model integration
- SQLite — persistent history
- Pandas — result table and CSV export
- Git / GitHub — version control and submission

## Project structure

```text
ai-test-case-generator-agent/
├── app.py
├── agent.py
├── test_case_generator.py
├── prompts.py
├── database.py
├── export_utils.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation (Windows / VS Code)

### 1. Install prerequisites

Install Python 3.10+ and Ollama:
https://ollama.com/download

### 2. Download the local model

Open a terminal and run:

```powershell
ollama pull llama3.2
```

Keep Ollama running. If required, start it in a separate terminal:

```powershell
ollama serve
```

### 3. Create and activate a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 4. Install dependencies

```powershell
pip install -r requirements.txt
```

### 5. Start the application

```powershell
streamlit run app.py
```

Open the local URL displayed in the terminal, usually:
`http://localhost:8501`

## How to use

1. Enter a clear software requirement, such as a login or registration feature.
2. Select scenario types and the requested number of test cases.
3. Click **Generate test cases**.
4. Review the feature summary and assumptions.
5. Edit any generated fields or delete cases that are not needed.
6. Download the current results as CSV or save them to history.
7. Open the History tab to reload or delete previous runs.

## Agent workflow

1. `app.py` collects the requirement and user-selected scenario types.
2. `agent.py` validates the request and coordinates the model call using LangChain.
3. `prompts.py` instructs the local LLM to return a predictable JSON structure and not invent unspecified rules.
4. Ollama generates the feature summary, assumptions, and test cases.
5. `test_case_generator.py` validates required fields, scenario types, priorities, and duplicate titles, then assigns stable IDs.
6. Streamlit displays editable test cases.
7. `database.py` stores requirement and results in SQLite.
8. `export_utils.py` uses Pandas to create the CSV download.

## Database design

SQLite creates `test_cases.db` automatically. The `generation_runs` table stores:
- `id` — primary key
- `requirement` — original feature requirement
- `feature_summary` — agent's summary
- `assumptions_json` — assumptions as JSON
- `test_cases_json` — generated/edited test cases as JSON
- `model` — Ollama model name
- `created_at` — local timestamp

## Test checklist

| Test | Expected behaviour |
|---|---|
| Empty requirement | Ask user to enter a requirement |
| Registration requirement | Generate relevant registration cases |
| Login requirement | Generate login-specific cases |
| Negative scenarios | Include relevant invalid-input cases |
| Unclear requirement | State assumptions / points to confirm |
| Invalid LLM response | Show helpful error without crashing |
| Edit test case | Edited values appear in table and CSV |
| Delete test case | Selected case is removed |
| Save and reload history | Saved results remain after restart |
| CSV export | Download contains displayed test cases |

## Important quality note

AI-generated test cases are suggestions, not proof of actual application behaviour. A human tester must review each test case and confirm assumptions before using it in real testing. The model is instructed not to invent rules that are missing from the requirement.

## Viva preparation

**Why Ollama?** It runs the language model locally and avoids a paid hosted API.

**Why LangChain?** It provides a consistent chat-model interface for sending system and user messages to Ollama.

**Why SQLite?** It is lightweight, file-based, and keeps saved test runs available after restarting the app.

**Why Pandas?** It organizes test-case records into a table and exports them to CSV.

**What makes this an agent?** It analyzes a requirement, selects requested scenario categories, invokes the LLM, validates structured output, and uses storage/export tools to complete the workflow.

**Does it execute tests?** No. It generates manual test cases; actual test execution is outside this assignment.
