"""
Helper to handle OpenAI requests.
"""
import json
import time
from typing import Any, Dict, List, NamedTuple, Optional

import numpy as np
import numpy.typing as npt
import openai
from openai import InvalidRequestError

from server.common.env_variables import EnvVars, OpenAIPrices
from server.common.logger_helper import LOGGER
from server.helpers.openai_functions_helper import OPENAI_FUNCTIONS

# Type for Numpy Array
NumpyArray = npt.NDArray[np.float32]

CompletionMessages = List[Dict[str, str]]

_ONE_K_TOKENS = 1000.0


class ChatResponse(NamedTuple):
    """
    Chat Response NT representation
    """

    ok: bool = True
    response: str = ""
    error_message: str = None
    invalid_request: bool = False
    question_without_answer: bool = False


class EmbeddingResponse(NamedTuple):
    """
    Embedding Response NT representation
    """

    ok: bool = True
    embeddings: Optional[NumpyArray] = None
    error_message: str = None


class UsageCompletionStats(NamedTuple):
    """
    Usage Completion Stats NT representation
    """

    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


class UsageEmbeddingStats(NamedTuple):
    """
    Usage Embeddings Stats NT representation
    """

    input_tokens: int = 0
    total_tokens: int = 0


class OpenAIHelper:  # pylint: disable=too-few-public-methods
    """
    OpenAI wrapper for all openai related information
    """

    def __init__(self: "OpenAIHelper", config: EnvVars) -> None:
        """
        Default class constructor
        :param config: EnvVars object representing all needed information to connect and initialize
            Redis, OpenAI and set specific default values.
        :return: None
        """
        openai.api_key = config.openai.api_key
        self._openai_chat_model = config.openai.chat_model
        self._openai_embedding_model = config.openai.embedding_model
        self._retries: int = config.openai.retries
        self._retry_sleep_time: int = config.openai.retry_sleep_time
        self._openai_stats: bool = config.openai.stats
        self._openai_prices: OpenAIPrices = config.openai.prices
        self._openai_temperature: float = config.openai.temperature
        self._openai_top_priority: float = config.openai.top_priority
        self._completion_input: int = 0
        self._completion_output: int = 0
        self._completion_total: int = 0
        self._embeddings_input: int = 0
        self._embeddings_total: int = 0

        if config.openai.type is not None and config.openai.type == "azure":
            openai.api_type = config.openai.type
            openai.api_base = config.azure.api_base
            openai.api_version = config.azure.api_version

    def completion(self: "OpenAIHelper", messages: CompletionMessages) -> ChatResponse:
        """
        Creates a ChatCompletion object based on the 'messages'
        :param messages: Information to be used with the OpenAI
        :return: OpenAI response object
        """
        error_message = ""
        for retry in range(self._retries):
            try:
                completion = openai.ChatCompletion.create(  # type: ignore[no-untyped-call]
                    deployment_id=self._openai_chat_model,
                    temperature=self._openai_temperature,
                    top_p=self._openai_top_priority,
                    messages=messages
                )

                # Compute stats based on env var
                if self._openai_stats:
                    self.__compute_completion_usage(completion)

                response_message = completion["choices"][0]["message"]
                if response_message.get("function_call"):
                    function_name = response_message["function_call"]["name"]
                    function_args = json.loads(response_message["function_call"]["arguments"])
                    function_response = OPENAI_FUNCTIONS[function_name]["function_call"](
                        function_args
                    )  # type: ignore[operator]

                    return ChatResponse(response=function_response)

                return ChatResponse(response=response_message["content"])

            except InvalidRequestError as e:
                return ChatResponse(ok=False, invalid_request=True, error_message=str(e))
            except Exception as e:
                error_message = str(e)
                if retry < (self._retries - 1):
                    time.sleep(self._retry_sleep_time)

        return ChatResponse(ok=False, error_message=error_message)

    def encode_text(
        self: "OpenAIHelper",
        text: str,
    ) -> EmbeddingResponse:
        """
        Creates an embedding OpenAI object.
        :param text: Text to be encoded
        :return: OpenAI Embedding response
        """
        error_message = ""
        for retry in range(self._retries):
            try:
                response = openai.Embedding.create(  # type: ignore[no-untyped-call]
                    deployment_id=self._openai_embedding_model, input=[text]
                )

                # Compute stats based on env var
                if self._openai_stats:
                    self.__compute_embeddings_usage(response)

                return EmbeddingResponse(embeddings=np.array(response["data"][0]["embedding"]))

            except Exception as e:
                error_message = str(e)
                if retry < (self._retries - 1):
                    time.sleep(self._retry_sleep_time)

        return EmbeddingResponse(ok=False, error_message=error_message)

    @property
    def completion_stats(self: "OpenAIHelper") -> UsageCompletionStats:
        """
        Usage Completion stats class property
        :return: UsageCompletionStats NT representing the needed values.
        """
        return UsageCompletionStats(
            input_tokens=self._completion_input,
            output_tokens=self._completion_output,
            total_tokens=self._completion_total,
        )

    @property
    def embedding_stats(self: "OpenAIHelper") -> UsageEmbeddingStats:
        """
        Usage Embeddings stats class property
        :return: UsageEmbeddingStats NT representing the needed values.
        """
        return UsageEmbeddingStats(
            input_tokens=self._embeddings_input,
            total_tokens=self._embeddings_total,
        )

    def __compute_completion_usage(  # type: ignore[misc]
        self: "OpenAIHelper", completion: Dict[str, Any]
    ) -> None:
        """
        Computes and builds the completion's current usage calculation
        :param completion: Dictionary object returned by OpenAI.
        :return: None.
        """
        _input = completion["usage"]["prompt_tokens"]
        _output = completion["usage"]["completion_tokens"]
        _total = completion["usage"]["total_tokens"]

        _input_charges = _input * self._openai_prices.completion_input / _ONE_K_TOKENS
        _output_charges = _output * self._openai_prices.completion_output / _ONE_K_TOKENS
        _total_charges = _input_charges + _output_charges

        LOGGER.info(f"Completion Stats:")
        LOGGER.info(f"Input Tokens : {_input:>5} (U$D {_input_charges:.5f})")
        LOGGER.info(f"Output Tokens: {_output:>5} (U$D {_output_charges:.5f})")
        LOGGER.info(f"Total Tokens : {_total:>5} (U$D {_total_charges:.5f})")

        self._completion_input += _input
        self._completion_output += _output
        self._completion_total += _total

    def __compute_embeddings_usage(  # type: ignore[misc]
        self: "OpenAIHelper", embeddings: Dict[str, Any]
    ) -> None:
        """
        Computes and builds the embeddings' current usage calculation
        :param embeddings: Dictionary object returned by OpenAI.
        :return: None.
        """
        _input = embeddings["usage"]["prompt_tokens"]
        _total = embeddings["usage"]["total_tokens"]

        _total_charges = _total * self._openai_prices.embeddings / _ONE_K_TOKENS

        LOGGER.info(f"Embeddings Stats:")
        LOGGER.info(f"Total Tokens: {_total} (U$D {_total_charges:.8f})")

        self._embeddings_input += _input
        self._embeddings_total += _total
