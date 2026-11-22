import streamlit as st
import pandas as pd
from agent import TestCaseAgent, AgentError
from database import init_db, save_run, list_runs, get_run, delete_run
from export_utils import to_csv_bytes

st.set_page_config(page_title="AI Test Case Generator Agent", page_icon="🧪", layout="wide")
init_db()

st.markdown("""
<style>
.block-container {max-width: 1250px; padding-top: 1.6rem;}
.hero {padding: 1.5rem 1.8rem; border-radius: 16px; color: white;
background: linear-gradient(115deg,#142b4a,#286090); margin-bottom: 1.2rem;}
.hero h1 {color:white; margin:0;} .hero p {color:#e7eff8; margin:.4rem 0 0;}
div[data-testid="stMetric"] {background:#fff; padding:12px; border-radius:12px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>🧪 AI Test Case Generator Agent</h1><p>Turn plain-language software requirements into structured, editable manual test cases.</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Local AI settings")
    model_name = st.text_input("Ollama model", value="llama3.2")
    st.caption("Install and download the model locally before generating test cases.")
    st.divider()
    st.write("**Privacy:** Requirements are sent to your local Ollama service. Saved runs are stored in a local SQLite file.")
    st.caption("AI-generated test cases must be reviewed by a human before actual testing.")

tab_generate, tab_history, tab_help = st.tabs(["🧪 Generate test cases", "🗂️ History", "📘 Setup & help"])

def normalize_cases(cases):
    normalized = []
    for i, case in enumerate(cases, start=1):
        item = dict(case)
        item["test_case_id"] = str(item.get("test_case_id") or f"TC-{i:03d}")
        item["steps"] = item.get("steps", [])
        if isinstance(item["steps"], list):
            item["steps"] = "\n".join(str(x) for x in item["steps"])
        normalized.append(item)
    return normalized

with tab_generate:
    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        requirement = st.text_area(
            "Software requirement",
            height=240,
            placeholder="Example: A user should be able to register using name, email, and password. Email must be unique."
        )
        scenario_scope = st.multiselect(
            "Scenario types to include",
            ["Positive", "Negative", "Edge case"],
            default=["Positive", "Negative", "Edge case"]
        )
        count = st.slider("Number of test cases", min_value=3, max_value=20, value=8)
        generate = st.button("✨ Generate test cases", type="primary", use_container_width=True)

        if generate:
            if not requirement.strip():
                st.warning("Please enter a software requirement.")
            elif len(requirement.strip()) < 12:
                st.warning("Please provide more detail so the agent can understand the feature.")
            elif not scenario_scope:
                st.warning("Select at least one scenario type.")
            else:
                with st.spinner("Analyzing requirement and generating test cases with your local model..."):
                    try:
                        agent = TestCaseAgent(model_name)
                        result = agent.generate(requirement.strip(), scenario_scope, count)
                        st.session_state["current_requirement"] = requirement.strip()
                        st.session_state["current_cases"] = normalize_cases(result["test_cases"])
                        st.session_state["analysis"] = result.get("feature_summary", "")
                        st.session_state["assumptions"] = result.get("assumptions", [])
                        st.success(f"Generated {len(st.session_state['current_cases'])} test cases.")
                    except AgentError as e:
                        st.error(str(e))
                    except Exception as e:
                        st.error(f"Unexpected error: {e}")
                        st.info("Check that Ollama is running and the selected model is installed.")

    with col2:
        st.subheader("Requirement analysis")
        if st.session_state.get("analysis"):
            st.write(st.session_state["analysis"])
            assumptions = st.session_state.get("assumptions", [])
            if assumptions:
                st.markdown("**Assumptions / points to confirm**")
                for a in assumptions:
                    st.write(f"• {a}")
        else:
            st.info("The agent's feature summary and assumptions will appear here.")

    cases = st.session_state.get("current_cases", [])
    if cases:
        st.divider()
        st.subheader("Review and edit generated test cases")
        st.caption("Edit the fields below. Changes are reflected in the table, CSV export, and saved record.")
        for idx, case in enumerate(cases):
            with st.expander(f"{case.get('test_case_id','TC')} · {case.get('title','Untitled test case')}", expanded=(idx == 0)):
                c1, c2, c3 = st.columns([2, 2, 1])
                with c1:
                    case["title"] = st.text_input("Test case title", case.get("title", ""), key=f"title_{idx}")
                    case["scenario_type"] = st.selectbox(
                        "Scenario type", ["Positive", "Negative", "Edge case"],
                        index=["Positive", "Negative", "Edge case"].index(case.get("scenario_type", "Positive"))
                        if case.get("scenario_type") in ["Positive", "Negative", "Edge case"] else 0,
                        key=f"scenario_{idx}"
                    )
                with c2:
                    case["priority"] = st.selectbox(
                        "Priority", ["High", "Medium", "Low"],
                        index=["High", "Medium", "Low"].index(case.get("priority", "Medium"))
                        if case.get("priority") in ["High", "Medium", "Low"] else 1,
                        key=f"priority_{idx}"
                    )
                    case["preconditions"] = st.text_area("Preconditions", case.get("preconditions", ""), key=f"pre_{idx}", height=75)
                with c3:
                    st.write(f"**ID:** {case.get('test_case_id')}")
                    if st.button("🗑️ Delete", key=f"delete_case_{idx}"):
                        st.session_state["current_cases"].pop(idx)
                        st.rerun()
                case["steps"] = st.text_area("Test steps (one step per line)", case.get("steps", ""), key=f"steps_{idx}", height=110)
                case["test_data"] = st.text_area("Test data", case.get("test_data", ""), key=f"data_{idx}", height=70)
                case["expected_result"] = st.text_area("Expected result", case.get("expected_result", ""), key=f"expected_{idx}", height=80)
                case["assumptions"] = st.text_area("Case-specific assumptions", case.get("assumptions", ""), key=f"case_assumptions_{idx}", height=55)

        st.divider()
        st.subheader("Final test case table")
        display_rows = []
        for c in st.session_state["current_cases"]:
            display_rows.append({
                "ID": c.get("test_case_id"), "Scenario": c.get("scenario_type"),
                "Title": c.get("title"), "Preconditions": c.get("preconditions"),
                "Steps": c.get("steps"), "Test data": c.get("test_data"),
                "Expected result": c.get("expected_result"), "Priority": c.get("priority")
            })
        df = pd.DataFrame(display_rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
        left, middle, right = st.columns(3)
        with left:
            st.download_button("⬇️ Download CSV", data=to_csv_bytes(st.session_state["current_cases"]),
                               file_name="generated_test_cases.csv", mime="text/csv",
                               use_container_width=True)
        with middle:
            if st.button("💾 Save to history", type="primary", use_container_width=True):
                if not st.session_state["current_cases"]:
                    st.warning("There are no test cases to save.")
                else:
                    run_id = save_run(
                        st.session_state.get("current_requirement", requirement),
                        st.session_state["analysis"],
                        st.session_state["assumptions"],
                        st.session_state["current_cases"],
                        model_name
                    )
                    st.success(f"Saved successfully. Run ID: {run_id}")
        with right:
            if st.button("Clear results", use_container_width=True):
                for key in ["current_cases", "current_requirement", "analysis", "assumptions"]:
                    st.session_state.pop(key, None)
                st.rerun()

with tab_history:
    st.subheader("Saved generation history")
    runs = list_runs()
    if not runs:
        st.info("No saved runs yet. Generate test cases and select Save to history.")
    else:
        st.write(f"**{len(runs)} saved run(s)**")
        for run in runs:
            title = f"Run #{run['id']} · {run['created_at']} · {run['requirement'][:75]}"
            with st.expander(title):
                st.write("**Requirement**")
                st.write(run["requirement"])
                st.write("**Feature summary**")
                st.write(run["feature_summary"])
                hist_df = pd.DataFrame([{
                    "ID": c["test_case_id"], "Scenario": c["scenario_type"], "Title": c["title"],
                    "Preconditions": c["preconditions"], "Steps": c["steps"],
                    "Test data": c["test_data"], "Expected result": c["expected_result"],
                    "Priority": c["priority"]
                } for c in run["test_cases"]])
                st.dataframe(hist_df, use_container_width=True, hide_index=True)
                a, b = st.columns(2)
                with a:
                    st.download_button("Download this run as CSV", to_csv_bytes(run["test_cases"]),
                                       file_name=f"test_cases_run_{run['id']}.csv", mime="text/csv",
                                       key=f"download_run_{run['id']}")
                with b:
                    if st.button("Load into editor", key=f"load_run_{run['id']}"):
                        st.session_state["current_requirement"] = run["requirement"]
                        st.session_state["analysis"] = run["feature_summary"]
                        st.session_state["assumptions"] = run["assumptions"]
                        st.session_state["current_cases"] = normalize_cases(run["test_cases"])
                        st.success("Loaded. Open the Generate test cases tab to edit.")
                if st.button("Delete saved run", key=f"delete_run_{run['id']}"):
                    delete_run(run["id"])
                    st.rerun()

with tab_help:
    st.subheader("Installation and run instructions")
    st.markdown("""
**Prerequisites**
- Python 3.10 or newer
- Ollama installed and running
- A local model downloaded (default: `llama3.2`)

**Windows setup**
```powershell
# 1. Open this folder in VS Code / terminal
python -m venv .venv
.venv\\Scripts\\activate

# 2. Install packages
pip install -r requirements.txt

# 3. Download a local model (one time)
ollama pull llama3.2

# 4. Run the app
streamlit run app.py
```

If Ollama is not running, start it with `ollama serve` in a separate terminal. The app normally opens at `http://localhost:8501`.

**Data storage:** SQLite creates `test_cases.db` in this project folder. It is excluded from Git by `.gitignore`.
""")
    st.warning("AI output is a starting point, not proof of application behaviour. A tester must review test cases and confirm assumptions before execution.")
