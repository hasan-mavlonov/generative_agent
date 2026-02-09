"""Runtime configuration and prompt helpers for the backend server.

This module intentionally provides safe defaults so the project can run out of
box without requiring users to manually create a private ``utils.py`` first.
Environment variables can still override the key settings for real runs.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, Any

# Resolve all project paths relative to this file so execution works whether
# users run from repo root or from reverie/backend_server.
_BACKEND_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _BACKEND_DIR.parent.parent


def _resolve_path(value: str, default_relative_to_repo: str) -> str:
    """Return env override when present, otherwise a stable absolute default."""
    if value:
        return str(Path(value).expanduser())
    return str((_REPO_ROOT / default_relative_to_repo).resolve())


# OpenAI configuration (override with environment variables in real usage).
openai_api_key = os.getenv("OPENAI_API_KEY", "")
key_owner = os.getenv("KEY_OWNER", "")

# Filesystem paths used throughout the simulator.
maze_assets_loc = _resolve_path(
    os.getenv("MAZE_ASSETS_LOC", ""),
    "environment/frontend_server/static_dirs/assets",
)
env_matrix = _resolve_path(
    os.getenv("ENV_MATRIX", ""),
    "environment/frontend_server/static_dirs/assets/the_ville/matrix",
)
env_visuals = _resolve_path(
    os.getenv("ENV_VISUALS", ""),
    "environment/frontend_server/static_dirs/assets/the_ville/visuals",
)

fs_storage = _resolve_path(
    os.getenv("FS_STORAGE", ""), "environment/frontend_server/storage"
)
fs_temp_storage = _resolve_path(
    os.getenv("FS_TEMP_STORAGE", ""),
    "environment/frontend_server/temp_storage",
)

collision_block_id = os.getenv("COLLISION_BLOCK_ID", "32125")

# Verbose logging toggle.
debug = os.getenv("DEBUG", "true").strip().lower() in {"1", "true", "yes", "on"}


def generate_prompt(prompt_inputs: Iterable[Any], prompt_template: str) -> str:
    """Fill a prompt template by replacing ``!<INPUT n>!`` placeholders.

    ``prompt_inputs`` are injected positionally with 0-based indexes.
    """
    with open(prompt_template, "r", encoding="utf-8") as file_obj:
        prompt = file_obj.read()

    for index, value in enumerate(prompt_inputs):
        prompt = prompt.replace(f"!<INPUT {index}>!", str(value))

    if "<commentblockmarker>###</commentblockmarker>" in prompt:
        prompt = prompt.split("<commentblockmarker>###</commentblockmarker>", 1)[1]

    return prompt.strip()
