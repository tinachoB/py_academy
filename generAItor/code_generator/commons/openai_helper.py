"""
Helper to handle OpenAI requests.
"""
import logging
import time
from typing import Any, Dict, NamedTuple, Optional

import openai

from code_generator.commons.env_variables import EnvVars

LOGGER = logging.getLogger(__name__)

DEFAULT_RETRIES = 2
DEFAULT_RETRY_SLEEP_TIME = 5  # Seconds


class UsageStats(NamedTuple):
    completion_tokens: int = 0
    prompt_tokens: int = 0
    total_tokens: int = 0


class OpenAIHelper:  # pylint: disable=too-few-public-methods
    def __init__(self: "OpenAIHelper", env_vars: EnvVars) -> None:
        openai.api_key = env_vars.api_key
        self._openai_model = env_vars.openai_model
        self._engine = None
        self._completion_tokens: int = 0
        self._prompt_tokens: int = 0
        self._total_tokens: int = 0
        self._instruct_model_in_use = env_vars.openai_instruct_model_use

        if env_vars.openai_type is not None and env_vars.openai_type == "azure":
            openai.api_type = env_vars.openai_type
            openai.api_base = env_vars.azure_base
            openai.api_version = env_vars.azure_version
            self._engine = env_vars.azure_deployment_id

    def consume(
        self: "OpenAIHelper",
        prompt: str,
        show_error_log: bool = True,
        retries: int = DEFAULT_RETRIES,
        retry_sleep_time: int = DEFAULT_RETRY_SLEEP_TIME,
    ) -> Optional[str]:
        for retry in range(retries):
            try:
                return self._consume(prompt=prompt)
            except Exception as exc:
                if show_error_log:
                    LOGGER.error(f"Error: {exc}.")

                if retry < (retries - 1):
                    LOGGER.info(f"Waiting {retry_sleep_time} secs. to retry...")
                    time.sleep(retry_sleep_time)
        return None

    @property
    def stats(self: "OpenAIHelper") -> UsageStats:
        """
        OpenAI usage stats property
        """
        return UsageStats(
            total_tokens=self._total_tokens,
            prompt_tokens=self._prompt_tokens,
            completion_tokens=self._completion_tokens,
        )

    def _consume(self: "OpenAIHelper", prompt: str) -> Optional[str]:
        """
        Interacts with the openai library based on the instruct_model_use env var
        @param prompt: The prompt to be used as an openai input.
        @return: The openai result based on the prompt input.
        """
        output = ""
        if self._instruct_model_in_use:
            completion = openai.Completion.create(  # type: ignore[no-untyped-call]
                engine=self._engine,
                model=self._openai_model,
                temperature=0.1,
                top_p=0.1,
                prompt=prompt,
                max_tokens=5000,  # See if we need to adjust the response length (via env var)
            )

            output = completion["choices"][0].text

        else:
            completion = openai.ChatCompletion.create(  # type: ignore[no-untyped-call]
                engine=self._engine,
                model=self._openai_model,
                temperature=0.1,
                top_p=0.1,
                messages=[{"role": "system", "content": prompt}],
            )

            output = completion["choices"][0]["message"]["content"]

        self._compute_usage(completion)

        return output

    def _compute_usage(  # type: ignore[misc]
        self: "OpenAIHelper", completion: Dict[str, Any]
    ) -> None:
        if "usage" in completion:
            self._completion_tokens += completion["usage"]["completion_tokens"]
            self._prompt_tokens += completion["usage"]["prompt_tokens"]
            self._total_tokens += completion["usage"]["total_tokens"]
