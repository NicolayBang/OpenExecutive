from openexecutive.agents.base import BaseAgent
from openexecutive.agents.model_defaults import default_model


class ProductAgent(BaseAgent):
    name = "cpo"
    domain = "product"

    @property
    def model(self) -> str:  # type: ignore[override]
        return default_model()

    def get_system_prompt(self) -> str:
        from openexecutive.prompts.domain_prompts import CPO_PROMPT

        return CPO_PROMPT
