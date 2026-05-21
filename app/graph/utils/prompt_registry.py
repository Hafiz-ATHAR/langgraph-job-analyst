import logging
import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Protocol

import mlflow

from app.config import get_settings
from app.graph.utils.prompts import PROMPTS

logger = logging.getLogger(__name__)

_settings = get_settings()
mlflow.set_tracking_uri(_settings.mlflow_tracking_uri)


_VAR_PATTERN = re.compile(r"\{\{\s*(\w+)\s*\}\}")


class Prompt(Protocol):
    def format(self, **kwargs: Any) -> str: ...


@dataclass(frozen=True)
class LocalPrompt:
    """Fallback used when the MLflow Prompt Registry is unreachable.

    Renders MLflow-style ``{{var}}`` templates from the in-repo PROMPTS dict so
    local development without a running MLflow server is unblocked.
    """

    name: str
    template: str

    def format(self, **kwargs: Any) -> str:
        def replace(match: re.Match[str]) -> str:
            var = match.group(1)
            if var not in kwargs:
                raise KeyError(f"Missing variable '{var}' for prompt '{self.name}'")
            return str(kwargs[var])

        return _VAR_PATTERN.sub(replace, self.template)


@lru_cache
def _load(name: str, alias: str) -> Prompt:
    uri = f"prompts:/{name}@{alias}"
    try:
        return mlflow.genai.load_prompt(uri) # type: ignore
    except Exception as exc:
        if name not in PROMPTS:
            raise KeyError(f"Prompt '{name}' not found in MLflow registry or local PROMPTS") from exc
        logger.warning(
            "MLflow load_prompt(%s) failed (%s); falling back to local template for '%s'",
            uri,
            exc.__class__.__name__,
            name,
        )
        return LocalPrompt(name=name, template=PROMPTS[name])


def load_prompt(name: str) -> Prompt:
    return _load(name, _settings.prompt_alias)
