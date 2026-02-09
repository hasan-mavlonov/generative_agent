"""Runtime configuration and prompt helpers for the backend server.

This module intentionally provides safe defaults so the project can run out of
box without requiring users to manually create a private ``utils.py`` first.
Environment variables can still override the key settings for real runs.
"""

from __future__ import annotations

import os
from typing import Iterable, Any

# OpenAI configuration (override with environment variables in real usage).
openai_api_key = os.getenv("OPENAI_API_KEY", "")
key_owner = os.getenv("KEY_OWNER", "")

# Filesystem paths used throughout the simulator.
maze_assets_loc = os.getenv(
    "MAZE_ASSETS_LOC", "../../environment/frontend_server/static_dirs/assets"
)
env_matrix = os.getenv("ENV_MATRIX", f"{maze_assets_loc}/the_ville/matrix")
env_visuals = os.getenv("ENV_VISUALS", f"{maze_assets_loc}/the_ville/visuals")

fs_storage = os.getenv("FS_STORAGE", "../../environment/frontend_server/storage")
fs_temp_storage = os.getenv(
    "FS_TEMP_STORAGE", "../../environment/frontend_server/temp_storage"
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
