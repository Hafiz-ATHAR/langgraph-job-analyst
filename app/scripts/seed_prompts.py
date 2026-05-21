"""Sync local prompt templates to the MLflow Prompt Registry.

Idempotent: only registers a new version when the in-repo template differs
from the latest registered version. Promotes the configured alias to the
resulting version unless ``--no-promote`` is passed.

Usage:
    python -m app.scripts.seed_prompts
    python -m app.scripts.seed_prompts --alias staging
    python -m app.scripts.seed_prompts --no-promote
"""

import argparse
import logging
import sys

import mlflow

from app.config import get_settings
from app.graph.utils.prompts import PROMPTS

logger = logging.getLogger("seed_prompts")


def _latest_template(name: str) -> tuple[int, str] | None:
    """Return ``(version, template)`` of the latest registered version, or ``None``."""
    try:
        prompt = mlflow.genai.load_prompt(f"prompts:/{name}@latest")  # type: ignore
    except Exception:
        return None
    return prompt.version, prompt.template  # type: ignore


def sync_prompt(name: str, template: str, alias: str, promote: bool) -> None:
    latest = _latest_template(name)
    if latest is not None and latest[1] == template:
        version = latest[0]
        logger.info("'%s' unchanged at version %d — skipping register", name, version)
    else:
        commit_message = (
            f"Initial seed of '{name}'"
            if latest is None
            else f"Update '{name}' (was v{latest[0]})"
        )
        prompt = mlflow.genai.register_prompt(  # type: ignore
            name=name,
            template=template,
            commit_message=commit_message,
            tags={"source": "app.scripts.seed_prompts"},
        )
        version = prompt.version
        logger.info("Registered '%s' version %d", name, version)

    if promote:
        mlflow.genai.set_prompt_alias(name=name, alias=alias, version=version)  # type: ignore
        logger.info("Set alias '%s' -> '%s' v%d", name, alias, version)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--alias",
        default=None,
        help="Alias to point at the registered version (defaults to settings.prompt_alias).",
    )
    parser.add_argument(
        "--no-promote",
        action="store_true",
        help="Register the prompt but do not move the alias.",
    )
    args = parser.parse_args()

    settings = get_settings()
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment(settings.mlflow_experiment)
    alias = args.alias or settings.prompt_alias
    logger.info(
        "Seeding %d prompt(s) to %s", len(PROMPTS), settings.mlflow_tracking_uri
    )
    for name, template in PROMPTS.items():
        sync_prompt(
            name=name, template=template, alias=alias, promote=not args.no_promote
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
