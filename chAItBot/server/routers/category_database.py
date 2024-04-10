"""
Category Database routers methods
"""

from fastapi import APIRouter, HTTPException, Query, status, Security
from fastapi.params import Depends
from sqlalchemy import asc
from sqlalchemy.orm import Session

from server.Auth0.VerifyToken import VerifyToken
from server.common.common import error_detail, error_response
from server.common.env_variables import get_env_vars
from server.helpers.embeddings_db import EmbeddingsDB
from server.helpers.mysql_helper import get_db
from server.helpers.openai_helper import OpenAIHelper
from server.models.category_database import CategoriesModel
from server.models.knowledge_categories_database import KnowledgeBaseCategoriesModel
from server.models.questionwithoutanswers_categories_model import QuestionWithoutAnswersCategoriesModel
from server.schemas.category_database import (
    Category,
    CategoryBaseByIdRequest,
    CategoryBaseRequest,
    CategoryResponse,
    Pagination, GetCategoryById,
)
from server.schemas.wrappers.base_response import MessagePost, TResponseDataPost
from server.services.category_service import create_category_service, update_category_service
auth = VerifyToken()

router = APIRouter()

__env_vars = get_env_vars()
__openai_helper = OpenAIHelper(config=__env_vars)
__redis_helper = EmbeddingsDB(config=__env_vars.redis)
# __unanswered_questions = UnansweredQuestionsDB(config=get_env_vars().redis)


@router.get(path="/SearchCategory", response_model=CategoryResponse)
async def get_all_categories(auth_result: str = Security(auth.verify),
                             page: int = Query(description="Page number"),
    pageSize: int = Query(description="Number of items per page"),
    textToSearch: str = Query(
        None, description="Text to search in the database"
    ),
    db: Session = Depends(get_db),
) -> CategoryResponse:
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
        query = db.query(CategoriesModel)
        query = query.order_by(asc(CategoriesModel.Description))
        # Apply text search if texttosearch is provided
        if textToSearch:
            query = query.filter(CategoriesModel.Description.ilike(f"%{textToSearch}%"))

        total_results = query.count()
        total_pages = (
            total_results + pageSize - 1
        ) // pageSize  # Use integer division to get the total pages

        # Perform pagination
        offset = (page - 1) * pageSize

        categories: list[Category] = [
            Category(id=item.Id, description=item.Description)
            for item in query.offset(offset).limit(pageSize).all()
        ]

        pagination = Pagination(
            totalRecords=total_results, page=page, pageSize=pageSize, totalPages=total_pages
        )

        if categories == []:
            message.message = "No se encontraron resultados."
            message.status_code = 204

        if total_results <= 0:
            message.message = "No se encontraron resultados."
            message.status_code = 204
            message.errors.append(f"Operacion fallida: No se encontro registro con {textToSearch}.")

        # Ordenar la lista de objetos por el atributo 'nombre'


        return CategoryResponse(message=message, data=categories, pagination=pagination)
    except Exception as e:
        raise error_response(detail=str(e))


@router.post(path="/CreateCategory")
async def create_category(categoryRequest: CategoryBaseRequest, auth_result: str = Security(auth.verify), db: Session = Depends(get_db)):
    try:
        response = create_category_service(categoryRequest, db)
        return response
    except Exception as ex:
        return {"message": "Error en la solicitud."}


@router.put(path="/UpdateCategory")
async def create_category(categoryRequest: CategoryBaseByIdRequest, db: Session = Depends(get_db), auth_result: str = Security(auth.verify)):
    try:
        response = update_category_service(categoryRequest, db)
        return response
    except Exception as ex:
        return {"message": "Error en la solicitud."}


@router.delete(path="/DeleteCategory")
async def delete_category(id: int = Query(), db: Session = Depends(get_db), auth_result: str = Security(auth.verify)):
    """
    API DELETE method to delete category from the DB.
    \f
    :param id: The id of the category to be deleted.
    :param db: The current DB instance.
    """
    response = TResponseDataPost()
    try:
        category_knowledgebase_realtion = (
            db.query(KnowledgeBaseCategoriesModel).filter_by(Category_Id=id).first()
        )

        category_questionwithoutanswer_realtion = (
            db.query(QuestionWithoutAnswersCategoriesModel).filter_by(categoryId=id).first()
        )

        if category_knowledgebase_realtion is not None and category_questionwithoutanswer_realtion is not None:
            response.success = False
            response.message.errors.append("Esta categoría no se puede eliminar ya que se encuentra asociada a uno o más datos. Por favor, revisá la base de conocimiento.")
            response.message.errors.append("Esta categoría no se puede eliminar ya que se encuentra asociada a uno o más datos. Por favor, revisá las preguntas sin respuesta.")
            response.message.status_code = 409
        elif category_questionwithoutanswer_realtion is not None:
            response.success = False
            response.message.message = "Esta categoría no se puede eliminar ya que se encuentra asociada a uno o más datos. Por favor, revisá las preguntas sin respuesta."
            response.message.status_code = 409
        elif category_knowledgebase_realtion is not None:
            response.success = False
            response.message.message = "Esta categoría no se puede eliminar ya que se encuentra asociada a uno o más datos. Por favor, revisá la base de conocimiento."
            response.message.status_code = 409
        else:
            result = db.query(CategoriesModel).filter_by(Id=id).first()
            if result is not None:
                db.delete(result)
                db.commit()
                response.message.message = "La categoría se eliminó correctamente."
            else:
                response.message.errors.append(f"Operación fallida: No existe la categoría con ID {id}.")
                response.success = False
                response.message.message = "No existe el registro."
                response.message.status_code = 404

    except Exception as e:
        response.success = False
        response.message.message = "Operación fallida."

    return response


@router.get(path="/GetCategoryById", response_model=GetCategoryById)
async def get_category_by_id(
    id: int = Query(), db: Session = Depends(get_db), auth_result: str = Security(auth.verify)) -> GetCategoryById:
    """
    API GET method to return a category by its ID.
    :param id: The ID of the category to be retrieved.
    :param db: The current DB instance.
    :return: A response with the category data or an error message.
    """
    message = MessagePost()

    try:
        result = db.query(CategoriesModel).filter_by(Id=id).first()

        if result is not None:
            # Crear un objeto Category con los datos de la consulta
            response = Category(
                id=result.Id,
                description=result.Description
            )
        else:
            message.message = "No se encontraron resultados."
            message.status_code = 400
            response = {}

        return GetCategoryById(data=response, message=message)

    except Exception as e:
        message.status_code = 500
        return GetCategoryById(message=message)
