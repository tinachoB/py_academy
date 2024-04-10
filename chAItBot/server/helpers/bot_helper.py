"""
Bot helper methods and classes
"""
import datetime
from typing import NamedTuple, Optional, List
from fastapi.params import Depends
from sqlalchemy.orm import Session
from server.helpers.mysql_helper import get_db
from server.common.env_variables import AlgorithmsEnvVars
from server.common.logger_helper import LOGGER
from server.helpers.embeddings_db import EmbeddingsDB, SimilaritiesResult
from server.helpers.history_db import HistoryCache
from server.helpers.openai_helper import ChatResponse, CompletionMessages, OpenAIHelper
from server.helpers.prompt_helper import PromptHelper
from server.models.messages_database import MessagesModel
from server.models.unanswered_question import UnansweredQuestionModel


class QuestionResponse(NamedTuple):
    """
    A NT with the question's response information
    """

    ok: bool = True
    response: str = ""
    error_message: Optional[str] = None


class BotHelper:
    """
    Class representing the Bot main information and methods to interact with.
    """

    def __init__(  # pylint: disable=too-many-arguments
        self: "BotHelper",
        openai_helper: OpenAIHelper,
        embeddings_db: EmbeddingsDB,
        history: HistoryCache,
        algorithms_config: AlgorithmsEnvVars,
        history_count: int,
    ) -> None:
        """
        Default class constructor
        :param openai_helper: OpenAI object to extract information from
        :param embeddings_db: Embeddings DB object to extract information from
        :param history: History DB object to extract information from
        :param algorithms_config: Algorithms related configuration
        :param history_count: History count limit to be used
        """
        self._openai: OpenAIHelper = openai_helper
        self._embeddings_db: EmbeddingsDB = embeddings_db
        self._history_count: int = history_count
        self._algorithms_config: AlgorithmsEnvVars = algorithms_config
        self._history: HistoryCache = history

    @property
    def history(self: "BotHelper") -> HistoryCache:
        """
        Class property representing the current history
        :return: HistoryCache NT with all related information
        """
        return self._history

    def ask_question(
        self: "BotHelper", question: str, categories: List[int], prompt_helper: PromptHelper, db
    ) -> QuestionResponse:
        """
        Main function to orchestrate the user question with OpenAI and Redis
        :param question: The user question
        :param db: The current DB instance.
        :param categories: The categories to be queried.
        :param prompt_helper: The PromptHelper object
        :return: QuestionResponse NT with the specific result information
        """

        def _get_response() -> QuestionResponse:
            response = self._get_assistant_response(prompt=prompt, question=question)

            if response.ok:
                return QuestionResponse(response=response.response)

            if response.invalid_request:
                return QuestionResponse(response=prompt_helper.unanswered_question)

            return QuestionResponse(ok=False, error_message=response.error_message)

        try:
            similar_texts: SimilaritiesResult = self._find_similar_texts(text=question, categories=categories)

            query_greeting = db.query(MessagesModel).filter(MessagesModel.MessageTypeCode == "Saludo")
            result_greeting = query_greeting.first()
            greeting = result_greeting.Message

            query_no_response = db.query(MessagesModel).filter(MessagesModel.MessageTypeCode == "Sin respuesta")
            result_no_response = query_no_response.first()
            no_response = result_no_response.Message

            if similar_texts.ok:
                if similar_texts.similarities:
                    prompt = prompt_helper.render_prompt(texts=similar_texts.similarities, no_response=no_response, greeting=greeting)
                    return _get_response()

                else:
                    prompt = prompt_helper.render_unanswered_prompt(question=question, no_response=no_response, greeting=greeting)
                    return _get_response()

            return QuestionResponse(ok=False, error_message=similar_texts.error_message)

        except Exception as e:
            return QuestionResponse(ok=False, error_message=str(e))

    def update_history(self: "BotHelper", question: str, response: str) -> None:
        """
        Updates the current history considering the history count private value
        :param question: Question to be updated in the history DB
        :param response: Response to be updated in the history DB
        :return: None
        """
        self._history.append([question, response])
        if len(self._history) > self._history_count:
            self._history = self._history[1:]

        LOGGER.info(f"Updated history: {self._history}")

    def _find_similar_texts(self: "BotHelper", text: str, categories: List[int]) -> SimilaritiesResult:
        """
        Gets the similarities between the user's text and the current persisted embeddings texts.
        :param text: User text to be compared against.
        :return: SimilaritiesResult NT with the specific information about the result.
        """
        encoded_texts = self._openai.encode_text(text=text)
        if encoded_texts.ok:
            return self._embeddings_db.get_similarities(
                text_embeddings=encoded_texts.embeddings,
                categories=categories,
                top_elements=self._algorithms_config.top_k_elements,
                filter_precision=self._algorithms_config.embeddings_precision_filter,
            )
        return SimilaritiesResult(ok=False, error_message=encoded_texts.error_message)

    def _get_assistant_response(self: "BotHelper", prompt: str, question: str) -> ChatResponse:
        """
        Builds the assistant response with the question and the prompt considering the
        history DB.
        :param prompt: Specific prompt to interact with OpenAI.
        :param question: Specific question to ask OpenAI.
        :return: ChatResponse NT with the specific information.
        """
        message: CompletionMessages = [{"role": "system", "content": prompt}]

        for history in self._history:
            message.append({"role": "user", "content": history[0]})
            message.append({"role": "assistant", "content": history[1]})

        message.append({"role": "user", "content": question})
        LOGGER.info(f"Messages: {message}")
        return self._openai.completion(messages=message)
