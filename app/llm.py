"""app/llm.py - one small wrapper for two LLM providers (Groq and Gemini).

The rest of the project only calls:  ask_llm(system_prompt, user_prompt)
It does not need to know which provider is used. The provider, the model and
the secret API key all come from the .env file (never from the code).
"""
import os

import requests

try:  # python-dotenv reads the .env file into environment variables
    from dotenv import load_dotenv

    load_dotenv(override=True, encoding="utf-8-sig")
except ImportError:  # the app still works if variables are set in the terminal
    pass

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


class LLMError(Exception):
    """Raised when the LLM call cannot be completed (missing key, network, API error)."""


def provider_name() -> str:
    """Which provider is selected in .env (groq or gemini). Default: groq."""
    return os.getenv("LLM_PROVIDER", "groq").strip().lower()


def model_name() -> str:
    """Which model is selected in .env for the chosen provider."""
    if provider_name() == "gemini":
        return os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    return os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


def _get_key(env_name: str) -> str:
    key = os.getenv(env_name, "").strip()
    if not key or key.startswith("your_"):
        raise LLMError(
            f"{env_name} is missing. Copy .env.example to .env, paste your key there, "
            "and restart the server."
        )
    return key


def _post(provider: str, url: str, headers: dict, payload: dict, timeout: int) -> dict:
    """Send the HTTP request and return the JSON reply, or raise LLMError."""
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
    except requests.exceptions.RequestException as exc:
        raise LLMError(f"Could not reach the {provider} API ({type(exc).__name__}).") from exc
    if resp.status_code != 200:
        hint = ""
        if resp.status_code in (401, 403):
            hint = " Check that your API key is correct."
        elif resp.status_code == 429:
            hint = " Rate limit reached. Wait a minute and try again."
        raise LLMError(f"{provider} API error {resp.status_code}.{hint} {resp.text[:200]}")
    try:
        return resp.json()
    except ValueError as exc:
        raise LLMError(f"{provider} API returned something that is not JSON.") from exc


def _ask_groq(system_prompt: str, user_prompt: str, temperature: float, json_mode: bool, timeout: int) -> str:
    payload = {
        "model": model_name(),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    headers = {"Authorization": f"Bearer {_get_key('GROQ_API_KEY')}", "Content-Type": "application/json"}
    data = _post("Groq", GROQ_URL, headers, payload, timeout)
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMError("Groq reply had an unexpected shape.") from exc


def _ask_gemini(system_prompt: str, user_prompt: str, temperature: float, json_mode: bool, timeout: int) -> str:
    generation_config = {"temperature": temperature}
    if json_mode:
        generation_config["responseMimeType"] = "application/json"
    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "generationConfig": generation_config,
    }
    headers = {"x-goog-api-key": _get_key("GEMINI_API_KEY"), "Content-Type": "application/json"}
    url = GEMINI_URL.format(model=model_name())
    data = _post("Gemini", url, headers, payload, timeout)
    try:
        parts = data["candidates"][0]["content"]["parts"]
        return "".join(p.get("text", "") for p in parts)
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMError("Gemini reply had an unexpected shape (it may have been blocked).") from exc


def ask_llm(system_prompt: str, user_prompt: str, temperature: float = 0.2,
            json_mode: bool = True, timeout: int = 30) -> str:
    """Send a system prompt and a user prompt to the chosen provider; return the text reply.

    temperature 0.2 = calm and consistent answers (good for facts).
    json_mode=True asks the provider to return valid JSON only.
    """
    provider = provider_name()
    if provider == "groq":
        return _ask_groq(system_prompt, user_prompt, temperature, json_mode, timeout)
    if provider == "gemini":
        return _ask_gemini(system_prompt, user_prompt, temperature, json_mode, timeout)
    raise LLMError(f"Unknown LLM_PROVIDER '{provider}'. Use 'groq' or 'gemini'.")

