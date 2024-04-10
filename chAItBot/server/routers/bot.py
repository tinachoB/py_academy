"""
Bot routers methods
"""
import datetime
import uuid

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import Null
from sqlalchemy.orm import Session
from fastapi.params import Depends
from server.helpers.mysql_helper import get_db

from server.common.bot_stats import BotStats
from server.common.common import error_detail, error_response
from server.common.env_variables import get_env_vars
from server.common.logger_helper import LOGGER
from server.helpers.bot_helper import BotHelper
from server.helpers.embeddings_db import EmbeddingsDB
from server.helpers.history_db import HistoryDB
from server.helpers.openai_helper import OpenAIHelper
from server.helpers.prompt_helper import PromptHelper
from server.helpers.unanswered_db import UnansweredQuestionsDB
from server.models.category_database import CategoriesModel
from server.models.history_detail_model import HistoryDetailModel
from server.models.history_model import HistoryModel
from server.models.models import BotStatistics, BotStatus, Question, BotResponse, Data
from server.models.questionwithoutanswers_categories_model import QuestionWithoutAnswersCategoriesModel
from server.models.unanswered_question import UnansweredQuestionModel

router = APIRouter()

__env_vars = get_env_vars()
__embeddings_db = EmbeddingsDB(config=__env_vars.redis)
__history_cache = HistoryDB(
    config=__env_vars.redis, expiration_time=__env_vars.history_expiration_time
)
__text_unanswered_question = "Lo siento, no tengo la información que estás buscando en este momento."
__unanswered_questions = UnansweredQuestionsDB(config=__env_vars.redis)
__prompt_helper = PromptHelper(assets=__env_vars.assets)
__stats_helper = BotStats(prices=__env_vars.openai.prices)


@router.get(
    path="/status",
    responses={
        status.HTTP_200_OK: {
            "model": BotStatus,
            "description": "The bot is up and running.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Something went wrong with the server.",
            "content": error_detail(),
        },
    },
)
async def bot_status() -> BotStatus:
    """
    API GET method to return the current status of the bot.
    \f
    :return: A NT representing the current bot status
    """
    try:
        return BotStatus(
            knowledge_database_size=__embeddings_db.size,
            unanswered_questions_size=__unanswered_questions.size,
        )
    except Exception as e:
        raise error_response(str(e))


@router.get(
    path="/stats",
    responses={
        status.HTTP_200_OK: {
            "model": BotStatistics,
            "description": "Gets the current statistics.",
        },
        status.HTTP_412_PRECONDITION_FAILED: {
            "description": "Statistics are not enabled via config.",
            "content": error_detail("Statistics are not enabled via config."),
        },
    },
)
async def bot_statistics() -> BotStatistics:
    """
    API GET method to return the current bot statistics.
    \f
    :return: A NT representing the current bot status
    """
    if __env_vars.openai.stats:
        return __stats_helper.stats

    raise HTTPException(
        status_code=status.HTTP_412_PRECONDITION_FAILED,
        detail="Statistics are not enabled via config.",
    )


@router.post(
    path="/ChatbotQuestion",
    responses={
        status.HTTP_200_OK: {
            "model": BotResponse,
            "description": "The question was answered successfully",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Error trying to answer the question.",
            "content": error_detail(),
        },
    },
)
async def bot_answer_question(body: Question, db: Session = Depends(get_db)) -> BotResponse:
    """
    API POST method to answer the user question.
    \f
    :param body: Current question to be added.
    :return: Dictionary representing the current api response.
    """
    try:
        if __env_vars.openai.stats:
            __stats_helper.inc_question()

        if body.session_id:
            session_id = body.session_id
            history = __history_cache.get(key=session_id)
        else:
            session_id = str(uuid.uuid1())
            history = []

        LOGGER.info(f"Incoming question: {body}")
        openai_helper = OpenAIHelper(config=__env_vars)

        bot_helper = BotHelper(
            openai_helper=openai_helper,
            embeddings_db=__embeddings_db,
            history=history,
            algorithms_config=__env_vars.algorithms,
            history_count=__env_vars.history_cache_count,
        )

        response = bot_helper.ask_question(question=body.question, categories=body.categoriesId, prompt_helper=__prompt_helper,
                                           db=db)

        if __env_vars.openai.stats:
            __stats_helper.inc_embeddings(stats=openai_helper.embedding_stats)
            __stats_helper.inc_completions(stats=openai_helper.completion_stats)

        if response.ok:

            if body.session_id:
                added_history = db.query(HistoryModel).filter_by(Session=session_id).first()
            else:
                added_history = HistoryModel(CreateOn=datetime.datetime.utcnow(), Session=session_id)

            history_by_session = db.query(HistoryModel).filter_by(Session=session_id).first()

            if not history_by_session:
                db.add(added_history)
                db.commit()

            added_question = None
            if __text_unanswered_question in response.response:
                create_question = True
                for cat in body.categoriesId:
                    category_exist = db.query(CategoriesModel).filter_by(Id=cat).first()
                    if category_exist is None:
                        create_question = False

                if create_question:
                    added_question = UnansweredQuestionModel(Content=body.question, Resolved=False,
                                                             CreatedOn=datetime.datetime.now())
                    db.add(added_question)
                    db.commit()
                    for cat in body.categoriesId:
                        added_question_category = QuestionWithoutAnswersCategoriesModel(
                            questionId=added_question.id,
                            categoryId=cat
                        )

                        db.add(added_question_category)

                    db.commit()

            if added_history:
                QuestionWithoutAnswer_Id = added_question.id if added_question is not None else None
                added_history_detail = HistoryDetailModel(Question=body.question, Answer=response.response,
                                                          CreateOn=datetime.datetime.utcnow(),
                                                          History_Id=added_history.Id if added_history.Id is not None else history_by_session.Id,
                                                          QuestionWithoutAnswer_Id=QuestionWithoutAnswer_Id)
                db.add(added_history_detail)
                db.commit()

            if response.response == __prompt_helper.unanswered_question:
                __unanswered_questions.set(question=body.question)
            else:
                bot_helper.update_history(question=body.question, response=response.response)
                __history_cache.set(key=session_id, value=bot_helper.history)

            LOGGER.info(f"Response: {response.response}")
            data = Data(
                answer=response.response,
                session_id=session_id
            )
            return BotResponse(data=data)

        LOGGER.error(response.error_message)
        raise error_response(detail=str(response.error_message))

    except HTTPException as e:
        LOGGER.error(e)
        raise e
    except Exception as e:
        LOGGER.error(e)
        raise error_response(detail=str(e))
