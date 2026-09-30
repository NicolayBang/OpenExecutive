from openexecutive.agents.base import BaseAgent
from openexecutive.agents.model_defaults import default_model


class HRAgent(BaseAgent):
    name = "chro"
    domain = "hr"

    @property
    def model(self) -> str:  # type: ignore[override]
        return default_model()

    def get_system_prompt(self) -> str:
        from openexecutive.prompts.domain_prompts import CHRO_PROMPT

        return CHRO_PROMPT
