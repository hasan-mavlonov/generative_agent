"""
Modernized wrapper for OpenAI Python SDK (v1+) using the Responses API.
Compatible replacement for the repo's legacy gpt_structure.py patterns.
"""
import json
import time
from typing import Callable, Optional

from openai import OpenAI
from utils import openai_api_key  # your repo already has this


def _resolve_api_key() -> Optional[str]:
    key = (openai_api_key or "").strip()
    return key or None


def _get_client() -> OpenAI:
    """Build an OpenAI client that never sends an empty Bearer token.

    Passing ``api_key=""`` causes httpx/httpcore to fail with
    ``Illegal header value b'Bearer '``. We normalize empty keys to ``None`` so
    the SDK can read ``OPENAI_API_KEY`` directly from the environment, and we
    provide a clear actionable error when no key is configured.
    """
    api_key = _resolve_api_key()
    if api_key is None:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Export a valid key before running the "
            "simulation (for example: `export OPENAI_API_KEY=...`)."
        )
    return OpenAI(api_key=api_key)

def temp_sleep(seconds: float = 0.1):
    time.sleep(seconds)

def _responses_text(resp) -> str:
    # OpenAI SDK exposes a convenience string for concatenated text output
    return getattr(resp, "output_text", None) or ""

def ChatGPT_single_request(prompt: str, model: str = "gpt-4o-mini") -> str:
    temp_sleep()
    client = _get_client()
    resp = client.responses.create(
        model=model,
        input=prompt,
    )
    return _responses_text(resp)

def GPT4_request(prompt: str, model: str = "gpt-4o") -> str:
    temp_sleep()
    try:
        client = _get_client()
        resp = client.responses.create(
            model=model,
            input=prompt,
        )
        return _responses_text(resp)
    except Exception:
        print("ChatGPT ERROR")
        return "ChatGPT ERROR"

def ChatGPT_request(prompt: str, model: str = "gpt-4o-mini") -> str:
    try:
        client = _get_client()
        resp = client.responses.create(
            model=model,
            input=prompt,
        )
        return _responses_text(resp)
    except Exception:
        print("ChatGPT ERROR")
        return "ChatGPT ERROR"

def GPT4_safe_generate_response(
    prompt: str,
    example_output,
    special_instruction: str,
    repeat: int = 3,
    fail_safe_response: str = "error",
    func_validate: Optional[Callable] = None,
    func_clean_up: Optional[Callable] = None,
    verbose: bool = False,
    model: str = "gpt-4o",
):
    # Old code asked model to output JSON; we keep the same approach.
    wrapped = 'GPT Prompt:\n"""\n' + prompt + '\n"""\n'
    wrapped += f"Output the response to the prompt above in json. {special_instruction}\n"
    wrapped += "Example output json:\n"
    wrapped += '{"output": "' + str(example_output) + '"}'

    if verbose:
        print("CHAT GPT PROMPT")
        print(wrapped)

    for i in range(repeat):
        try:
            raw = GPT4_request(wrapped, model=model).strip()
            end_index = raw.rfind("}") + 1
            raw = raw[:end_index]
            out = json.loads(raw)["output"]

            if func_validate is None or func_validate(out, prompt=wrapped):
                return func_clean_up(out, prompt=wrapped) if func_clean_up else out

            if verbose:
                print("---- repeat count:\n", i, out)
                print("~~~~")
        except Exception:
            pass

    return False

def ChatGPT_safe_generate_response(
    prompt: str,
    example_output,
    special_instruction: str,
    repeat: int = 3,
    fail_safe_response: str = "error",
    func_validate: Optional[Callable] = None,
    func_clean_up: Optional[Callable] = None,
    verbose: bool = False,
    model: str = "gpt-4o-mini",
):
    wrapped = '"""\n' + prompt + '\n"""\n'
    wrapped += f"Output the response to the prompt above in json. {special_instruction}\n"
    wrapped += "Example output json:\n"
    wrapped += '{"output": "' + str(example_output) + '"}'

    if verbose:
        print("CHAT GPT PROMPT")
        print(wrapped)

    for i in range(repeat):
        try:
            raw = ChatGPT_request(wrapped, model=model).strip()
            end_index = raw.rfind("}") + 1
            raw = raw[:end_index]
            out = json.loads(raw)["output"]

            if func_validate is None or func_validate(out, prompt=wrapped):
                return func_clean_up(out, prompt=wrapped) if func_clean_up else out

            if verbose:
                print("---- repeat count:\n", i, out)
                print("~~~~")
        except Exception:
            pass

    return False

def get_embedding(text: str, model: str = "text-embedding-3-small"):
    # Replaces text-embedding-ada-002 with current embedding models.
    # (You can also use text-embedding-3-large.)
    text = (text or "").replace("\n", " ").strip()
    if not text:
        text = "this is blank"
    client = _get_client()
    resp = client.embeddings.create(model=model, input=text)
    return resp.data[0].embedding
