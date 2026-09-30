from openexecutive.agents.base import BaseAgent
from openexecutive.agents.model_defaults import deep_reasoning_model


class FinanceAgent(BaseAgent):
    name = "cfo"
    domain = "finance"
    use_deep_reasoning = True

    @property
    def model(self) -> str:  # type: ignore[override]
        return deep_reasoning_model()

    def get_system_prompt(self) -> str:
        from openexecutive.prompts.domain_prompts import CFO_PROMPT

        return CFO_PROMPT
