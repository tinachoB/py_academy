"""
Helper to render the prompt
"""
from typing import List

from server.common.env_variables import AssetsEnvVars
from server.common.singleton import Singleton


class PromptHelper(metaclass=Singleton):
    """
    Class representing all Prompt needed information and methods
    """

    def __init__(self: "PromptHelper", assets: AssetsEnvVars):
        """
        Default class constructor.
        """
        with open(assets.prompt_template_path, encoding="utf8") as prompt:
            self._prompt: str = prompt.read()

        with open(
            assets.unanswered_question_default_response_path, encoding="utf8"
        ) as unanswered_question:
            self._unanswered_question: str = unanswered_question.read()



        with open(assets.no_embeddings_kb_default_values_path, encoding="utf8") as no_embeddings:
            self._no_embeddings_kb_values: str = no_embeddings.read()

    def render_prompt(self: "PromptHelper", texts: List[str], no_response: str, greeting: str) -> str:
        """
        Renders the specific prompt based on the texts' parameter.
        :param texts: Texts to be rendered.
        :param no_response: Text for when the bot doesnt know the answer.
        :return: None
        """
        return self._prompt.replace("[KNOWLEDGE_BASE]", "\n".join(texts)).replace("[UNANSWERED_QUESTION_DEFAULT_RESPONSE]", self._unanswered_question).replace("[NO_RESPONSE]", no_response).replace("[GREETINGS]", greeting)

    def render_unanswered_prompt(self: "PromptHelper", question: str, no_response: str, greeting: str) -> str:
        """
        Renders the specific prompt based on the texts' parameter.
        :param question: The unanswered question.
        :param no_response: Text for when the bot doesnt know the answer.
        :return: None
        """
        texts = [self._no_embeddings_kb_values.replace("[UNANSWERED_QUESTION]", question).replace("[UNANSWERED_QUESTION_DEFAULT_RESPONSE]", no_response)]
        return self.render_prompt(texts=texts, no_response=no_response, greeting=greeting)

    @property
    def unanswered_question(self: "PromptHelper") -> str:
        """
        Class property representing the unanswered question file's content
        :return: the unanswered question file's content
        """
        return self._unanswered_question
