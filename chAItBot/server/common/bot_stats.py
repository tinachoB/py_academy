"""
Bot stats common methods
"""

from server.common.env_variables import OpenAIPrices
from server.helpers.openai_helper import UsageCompletionStats, UsageEmbeddingStats
from server.models.models import BotStatistics, BotStatisticsItem, CompletionsBotStatistics

_ONE_K_TOKENS = 1000.0
_ROUND_DECIMALS = 7


class BotStats:
    """
    Class used to manage stats related information and methods
    """

    def __init__(self: "BotStats", prices: OpenAIPrices) -> None:
        """
        Default constructor class
        :prices: OpenAI related prices
        :return: None
        """
        self._prices: OpenAIPrices = prices
        self._questions_count: int = 0
        self._embeddings_tokens: int = 0
        self._completions_input_tokens: int = 0
        self._completions_output_tokens: int = 0
        self._completions_total_tokens: int = 0

    def inc_question(self: "BotStats") -> None:
        """
        Increments the questions count value
        :return: None
        """
        self._questions_count += 1

    def inc_embeddings(self: "BotStats", stats: UsageEmbeddingStats) -> None:
        """
        Increments the embeddings usage stats.
        :param stats: Stats values to increment with
        :return: None
        """
        self._embeddings_tokens += stats.total_tokens

    def inc_completions(self: "BotStats", stats: UsageCompletionStats) -> None:
        """
        Increments completions values (input, output, total)
        :param stats: Stats values to increment with
        :return None
        """
        self._completions_input_tokens += stats.input_tokens
        self._completions_output_tokens += stats.output_tokens
        self._completions_total_tokens += stats.total_tokens

    @property
    def stats(self: "BotStats") -> BotStatistics:
        """
        Stats class property
        :return: BotStatistics NT with all needed stats' information.
        """
        _completion_input_charges = round(
            self._completions_input_tokens * self._prices.completion_input / _ONE_K_TOKENS,
            _ROUND_DECIMALS,
        )
        _completion_output_charges = round(
            self._completions_output_tokens * self._prices.completion_output / _ONE_K_TOKENS,
            _ROUND_DECIMALS,
        )
        return BotStatistics(
            questions_count=self._questions_count,
            embeddings=BotStatisticsItem(
                tokens=self._embeddings_tokens,
                charges=round(
                    self._embeddings_tokens * self._prices.embeddings / _ONE_K_TOKENS,
                    _ROUND_DECIMALS,
                ),
            ),
            completions=CompletionsBotStatistics(
                input=BotStatisticsItem(
                    tokens=self._completions_input_tokens,
                    charges=_completion_input_charges,
                ),
                output=BotStatisticsItem(
                    tokens=self._completions_output_tokens,
                    charges=_completion_output_charges,
                ),
                total=BotStatisticsItem(
                    tokens=self._completions_total_tokens,
                    charges=round(
                        _completion_input_charges + _completion_output_charges, _ROUND_DECIMALS
                    ),
                ),
            ),
        )
