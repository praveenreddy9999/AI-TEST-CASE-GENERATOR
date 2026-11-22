import json
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from prompts import SYSTEM_PROMPT, build_generation_prompt
from test_case_generator import validate_generation

class AgentError(Exception):
    """Safe, user-readable agent error."""

class TestCaseAgent:
    def __init__(self, model_name="llama3.2"):
        self.model_name = (model_name or "llama3.2").strip()
        self.llm = ChatOllama(model=self.model_name, temperature=0.15, format="json")

    def generate(self, requirement, scenario_types, count=8):
        if not isinstance(requirement, str) or len(requirement.strip()) < 12:
            raise AgentError("Please enter a clear software requirement with enough detail.")
        if not scenario_types:
            raise AgentError("Select at least one scenario type.")
        prompt = build_generation_prompt(requirement, scenario_types, count)
        try:
            response = self.llm.invoke([
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=prompt)
            ])
            content = response.content
            if isinstance(content, list):
                content = "".join(str(x) for x in content)
            data = json.loads(content)
        except Exception as exc:
            detail = str(exc)
            low = detail.lower()
            if any(word in low for word in ["connection", "refused", "ollama", "connecterror"]):
                raise AgentError(
                    f"Cannot connect to Ollama or model '{self.model_name}'. "
                    f"Start Ollama and run `ollama pull {self.model_name}`. Details: {detail[:220]}"
                )
            raise AgentError(f"The model response could not be read as valid JSON. Please retry. Details: {detail[:220]}")
        try:
            return validate_generation(data, count)
        except ValueError as exc:
            raise AgentError(f"The model returned incomplete or invalid test cases: {exc}")
