"""
Unanswered Questions routers methods
"""
from typing import List, Type, cast, Optional, Union, Any

from fastapi import APIRouter, Query, Security
from fastapi.params import Depends
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta
import schedule
import threading
import time
import logging

from contextlib import contextmanager

from server.Auth0.VerifyToken import VerifyToken
from server.common.common import error_response
from server.common.env_variables import get_env_vars
from server.helpers.mysql_helper import get_db, SessionLocal
from server.helpers.unanswered_db import UnansweredQuestionsDB
from server.models import history_detail_model
from server.models.category_database import CategoriesModel
from server.models.history_detail_model import HistoryDetailModel
from server.models.history_model import HistoryModel
from server.models.questionwithoutanswers_categories_model import QuestionWithoutAnswersCategoriesModel
from server.models.unanswered_question import UnansweredQuestionModel
from server.schemas.no_results import NoResultsResponse
from server.schemas.unanswered_question import (
    Pagination,
    UnansweredQuestion,
    UnansweredQuestionRequest,
    UnansweredQuestionResponse, GetUnansweredQuestionById, QuestionResponse, GetHistoryDetailResponse, Categories,
)
from server.schemas.wrappers.base_response import MessagePost, TResponseDataPost, TResponseDataGet


auth = VerifyToken()
router = APIRouter()

__unanswered_questions = UnansweredQuestionsDB(config=get_env_vars().redis)


@router.get(path="/SearchQuestion", response_model=UnansweredQuestionResponse)
async def get_all_categories(
    auth_result: str = Security(auth.verify),
    page: int = Query(description="Page number"),
    pageSize: int = Query(description="Number of items per page"),
    textToSearch: str = Query(None, description="Text to search in the database"),
    hideResolved: bool = Query(None, description="Filter by resolved status"),
    categoryId: Optional[Any] = Query(None, description="Filter by category ID"),
    db: Session = Depends(get_db),
) -> UnansweredQuestionResponse:
    categoryId = None if categoryId == "" else categoryId

    """
    API GET method to return a list with the unanswered questions.
    \f
    :param db: The current DB instance.
    :param page: Page number for pagination (default is 1).
    :param pageSize: Number of items per page (default is 10).
    :param textToSearch: Text to search in the database.
    :return: A response that includes a message and a list of unanswered questions.
    """
    message = MessagePost()
    try:
        query = db.query(UnansweredQuestionModel).all()

        if textToSearch:
            query = [q for q in query if textToSearch.lower() in q.Content.lower()]
            if len(query) == 0:
                message.errors.append(f"Operacion fallida: No se encontró pregunta con {textToSearch}.")

        if hideResolved is not None:
            if hideResolved:
                query = [q for q in query if not q.Resolved]

            if len(query) == 0:
                message.errors.append(
                    f"Operacion fallida: No se encontró pregunta con hideResolved {hideResolved}.")

        if categoryId is not None:
            nuevo_array_principal = []
            categoryIdInt = int(categoryId)
            for registro in query:
                # Obtener el array question_category de cada registro
                if hasattr(registro, 'question_category'):
                    question_category = registro.question_category

                    question_category_filtrado = [item for item in question_category if
                                                  item.categoryId == categoryIdInt]

                    if question_category_filtrado:
                        nuevo_array_principal.append(registro)

            query = []
            query = nuevo_array_principal

            if len(query) == 0:
                message.errors.append(f"Operacion fallida: No se encontró pregunta con categoryId {categoryId}.")

        total_results = len(query)
        total_pages = (
            total_results + pageSize - 1
        ) // pageSize  # Use integer division to get the total pages
        offset = (page - 1) * pageSize

        unansweredquestion = []

        for item in query[offset: offset + pageSize]:
            categories = [
                Categories(id=item2.categories.Id, description=item2.categories.Description)
                for item2 in item.question_category
            ]

            question = UnansweredQuestion(
                id=item.id,
                content=item.Content,
                resolved=item.Resolved,
                createdOn=item.CreatedOn.strftime('%H:%M %d/%m/%Y'),
                categories=categories
            )
            unansweredquestion.append(question)

        pagination = Pagination(
            totalRecords=total_results, page=page, pageSize=pageSize, totalPages=total_pages
        )
        if total_results <= 0:
            message.message = "No se encontraron resultados."
            message.status_code = 204

        return UnansweredQuestionResponse(message=message, data=unansweredquestion, pagination=pagination)
    except Exception as e:
        raise error_response(detail=str(e))


@router.get("/GetQuestionById", response_model=GetUnansweredQuestionById)
async def get_category_by_id(
        id: int = Query(..., alias="id", description="ID of the category to be retrieved"),

        db: Session = Depends(get_db), auth_result: str = Security(auth.verify)) -> GetUnansweredQuestionById:
    """
    API GET method to return a category by its ID.
    :param id: The ID of the category to be retrieved.
    :param db: The current DB instance.
    :return: A response with the category data or an error message.
    """
    message = MessagePost()

    try:
        result = db.query(UnansweredQuestionModel).filter_by(id=id).first()

        if result is not None:
            # Crear un objeto Category con los datos de la consultaa
            categories: List[Categories] = [Categories(id=item.categories.Id, description=item.categories.Description) for item in result.question_category]
            response = UnansweredQuestion(
                id=result.id,
                content=result.Content,
                resolved=result.Resolved,
                createdOn=str(result.CreatedOn),
                categories=categories
            )
        else:
            message.message = "No se encontraron resultados."
            message.status_code = 204
            message.errors.append(f"Operación Fallida: No se encontró registro con Id {id}")
            response = {}

        return GetUnansweredQuestionById(data=response, message=message)

    except Exception as e:
        message.status_code = 500
        return GetUnansweredQuestionById(message=message)


@router.put(path="/SolveQuestion", response_model=TResponseDataPost)
async def update_unanswered_questions(
    id: int = Query(alias="id"),
    resolved: bool = Query(alias="resolved"),
    db: Session = Depends(get_db),
    auth_result: str = Security(auth.verify)
):
    """
    API PUT method to update an unanswered question.
    \f
    :param request: The request to be updated.
    :param db: The current DB instance.
    :return: A NT with the unanswered question.
    """
    message = MessagePost()

    message.message = "La pregunta se actualizó correctamente."
    response = TResponseDataPost(message=message)
    try:
        questionById = db.query(UnansweredQuestionModel).filter_by(id=id).first()

        if questionById:
            questionById.Resolved = resolved
            db.commit()
            db.refresh(questionById)
        else:
            response.success = False
            response.message.status_code = 404
            response.message.message = "No existe el registro."
            response.message.errors.append(f"Operación Fallida: No existe pregunta sin respuesta con ID {id}.")

    except Exception as ex:
        response.message.message = "Operación Fallida"
        response.message.status_code = 400
        db.rollback()
    finally:
        if questionById:
            db.refresh(questionById)

    return response



@router.delete(path="/DeleteQuestion")
async def delete_question(id: int = Query(), db: Session = Depends(get_db), auth_result: str = Security(auth.verify)):
    """
    API DELETE method to delete question from the DB.
    \f
    :param id: The id of the question to be deleted.
    :param db: The current DB instance.
    """
    response = TResponseDataPost()
    try:
        result = db.query(UnansweredQuestionModel).filter_by(id=id).first()
        if result is not None:
            (db.query(QuestionWithoutAnswersCategoriesModel).
                                       filter(QuestionWithoutAnswersCategoriesModel.questionId == id)).delete()
            db.delete(result)
            db.commit()
            response.message.message = "La pregunta se eliminó correctamente."
        else:
            response.message.errors.append(f"Operación fallida: No existe pregunta sin respuesta con ID {id}.")
            response.success = False
            response.message.message = "No existe el registro."
            response.message.status_code = 404
    except Exception as e:
        response.success = False
        response.message.message = "Operacion fallida."

    return response

def calcularfecha(fecha):
    # Obtener la fecha actual
    fecha_actual = datetime.now()

    # Calcular la diferencia de tiempo entre la fecha desconocida y la fecha actual
    diferencia_de_tiempo = fecha_actual - fecha

    # Verificar si la diferencia de tiempo es mayor a 3 meses
    return diferencia_de_tiempo > timedelta(days=90)

def delete_old_history(db: Session = Depends(get_db)):
    response = TResponseDataPost()
    try:
        # Lógica para borrar historiales mayores a 90 días
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        histories_to_delete = db.query(HistoryModel).filter(HistoryModel.CreateOn <= cutoff_date).all()

        # Crear una copia de la lista para evitar problemas al modificarla durante la iteración
        histories_to_delete_copy = list(histories_to_delete)

        for history in histories_to_delete_copy:
            unanswered_questions_to_delete = (
                db.query(UnansweredQuestionModel)
                .join(HistoryDetailModel)
                .filter(
                    HistoryDetailModel.History_Id == history.Id,
                    UnansweredQuestionModel.Resolved == False,
                    UnansweredQuestionModel.CreatedOn <= cutoff_date,
                )
                .all()
            )

            for question in unanswered_questions_to_delete:
                db.delete(question)

            db.delete(history)
            db.commit()

    except Exception as e:
        response.success = False
        response.message.message = "Operacion fallida."
    return response

def NotFound(data, id):
    data.message.errors.append(f"Operación fallida: No se encontró una pregunta sin respuesta con ID {id}.")
    data.data = None
    data.message.message = "No se encontró la pregunta."
    data.message.status_code = 204

    return data


@router.get(path="/GetHistoryDetail")
async def delete_question(id: int = Query(), db: Session = Depends(get_db), auth_result: str = Security(auth.verify)):
    """
    API DELETE method to delete question from the DB.
    \f
    :param id: The id of the question to be deleted.
    :param db: The current DB instance.
    """
    response = TResponseDataGet(data=[])
    try:
        result = db.query(UnansweredQuestionModel).filter_by(id=id).first()
        if result is not None:
            date = result.CreatedOn
            validate_fecha = calcularfecha(date)
            #Validar que la fecha de la pregunta sin respuesta no supere los 3 meses.
            if validate_fecha:
                response.message.message = "La pregunta tiene una antigüedad mayor a 3 meses, ya no se encuentra almacenado su historial."
                response.message.status_code = 409
                response.data = None
                return response
            #Pasó la validacion
            history_id = db.query(HistoryDetailModel).filter(HistoryDetailModel.QuestionWithoutAnswer_Id == id).first()
            if history_id:
                history = db.query(HistoryModel).filter(HistoryModel.Id == history_id.History_Id).first()
                history_details = sorted(history.history_details, key=lambda x: x.CreateOn, reverse=True)

                cant_details = 0
                for item in history_details:
                    if cant_details > 4:
                        break
                    mapper = GetHistoryDetailResponse(id=item.Id, question=item.Question, answer=item.Answer,
                                                      createdOn=str(item.CreateOn))
                    response.data.append(mapper)
                    cant_details += 1
            else:
                return NotFound(response, id)
        else:
            return NotFound(response, id)
    except Exception as e:
        response.success = False
        response.message.message = "Operacion fallida." #despliegue

    return response

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def delete_old_history_task():
    with get_db() as db:
        delete_old_history(db)

def run_background_task():
    while True:
        logging.info("Verificando tareas programadas...")
        schedule.run_pending()
        time.sleep(1)


# Iniciar la tarea programada diaria a las 2:00 AM
schedule.every().day.at("14:00").do(delete_old_history_task)

# Agregar una tarea programada para calcular la fecha
schedule.every().hour.do(calcularfecha)

# El hilo para ejecutar las tareas en segundo plano
background_thread = threading.Thread(target=run_background_task)
background_thread.start()




