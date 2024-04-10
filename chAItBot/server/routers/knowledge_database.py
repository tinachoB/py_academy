"""
Knowledge Database routers methods
"""
import datetime

from fastapi import APIRouter, HTTPException, Query, Response, status, Security
from fastapi.params import Depends
from mysqlx.protobuf import Message
from sqlalchemy.orm import Session, aliased, joinedload
from sqlalchemy import or_, and_

from server.Auth0.VerifyToken import VerifyToken
from server.common.common import create_redis_connection, error_detail, error_response
from server.common.env_variables import RedisEnvVars, get_env_vars
from server.helpers import openai_helper
from server.helpers.embeddings_db import EmbeddingsDB
from server.helpers.mysql_helper import get_db
from server.helpers.openai_helper import NumpyArray, OpenAIHelper
from server.models.category_database import CategoriesModel
from server.models.knowledge_categories_database import KnowledgeBaseCategoriesModel
from server.models.knowledge_database import KnowledgeDataBaseModel
from server.models.models import DatabaseResponse, DeleteDatabaseResponse
from server.models.unanswered_question import UnansweredQuestionModel
from server.schemas.category_database import Pagination, Category
from server.schemas.knowledge_database import (
    Categories,
    GetKnowledgeBase,
    GetKnowledgeBaseResponse,
    KnowledgeBaseRequest,
    KnowledgeDataBaseResponse,
    Pagination,
    UploadKnowledgeBaseRequest, Knowledge,
)
from server.schemas.wrappers.base_response import MessagePost, TResponseDataPost
from server.services.knowledge_database_service import (
    create_knowledgebase_service,
    update_knowledgebase_service, delete_knowledgebase,
)

auth = VerifyToken()
router = APIRouter()

__env_vars = get_env_vars()
__openai_helper = OpenAIHelper(config=__env_vars)
__redis_helper = EmbeddingsDB(config=__env_vars.redis)


@router.get(path="/SearchData", response_model=GetKnowledgeBaseResponse)
async def get_all_unanswered_questions(  # auth_result: str = Security(auth.verify),
        page: int = Query(description="Page number"),
        pageSize: int = Query(description="Number of items per page"),
        textToSearch: str = Query(
            None, description="Text to search in the database"
        ),
        categoryId: str = Query(None, description=""),
        db: Session = Depends(get_db),
) -> GetKnowledgeBaseResponse:
    message = MessagePost()
    result = None
    query_text_to_search = True
    try:
        tabla_media_knowledgecategories = aliased(KnowledgeBaseCategoriesModel)
        # condicion= lambda x : or_(x.Title.ilike(f"%{textToSearch}%"), x.Conent.ilike(f"%{textToSearch}%")), and_ (x.Id)

        if textToSearch:
            # 1er consulta
            query = db.query(KnowledgeDataBaseModel).filter(or_(KnowledgeDataBaseModel.Title.ilike(f"%{textToSearch}%"),
                                                                KnowledgeDataBaseModel.Content.ilike(
                                                                    f"%{textToSearch}%")), and_(
                CategoriesModel.Id == tabla_media_knowledgecategories.Category_Id,
                tabla_media_knowledgecategories.KnowledgeBase_Id == KnowledgeDataBaseModel.Id))

            if query.count() == 0:
                message.errors.append(f"Operacion fallida: No se encontro registro con {textToSearch}.")

        if categoryId:
            if textToSearch:
                # 2da consulta
                query = query.filter(CategoriesModel.Id == tabla_media_knowledgecategories.Category_Id,
                                     tabla_media_knowledgecategories.KnowledgeBase_Id == KnowledgeDataBaseModel.Id,
                                     CategoriesModel.Id == int(categoryId))
            else:
                # 1er consulta
                query = db.query(KnowledgeDataBaseModel).filter(
                    CategoriesModel.Id == tabla_media_knowledgecategories.Category_Id,
                    tabla_media_knowledgecategories.KnowledgeBase_Id == KnowledgeDataBaseModel.Id,
                    CategoriesModel.Id == int(categoryId))

            if query.count() == 0:
                message.errors.append(f"Operacion fallida: No se encontro registro con categoryId {categoryId}.")

        if not categoryId and not textToSearch:
            # 1er consulta si es que no viene ni category ni text to search
            query = db.query(KnowledgeDataBaseModel)

        total_results = query.count()
        total_pages = (total_results + pageSize - 1) // pageSize

        offset = (page - 1) * pageSize

        knowledge_base: list[GetKnowledgeBase] = []
        category_id: list[Category] = []
        for item in query.offset(offset).limit(pageSize).all():
            # Consultar las categorías relacionadas a este objeto
            # Consulta 2 o 3 ... n
            categories = (
                db.query(CategoriesModel)
                .filter(
                    CategoriesModel.Id == tabla_media_knowledgecategories.Category_Id,
                    tabla_media_knowledgecategories.KnowledgeBase_Id == item.Id,
                )
                .all()
            )

            # Crear una lista de objetos Categories con Id y Description
            category_list = [
                Categories(id=category.Id, description=category.Description)
                for category in categories
            ]

            categories_ordenadas = sorted(category_list, key=lambda x: x.description)

            knowledge_base.append(
                GetKnowledgeBase(
                    id=item.Id, title=item.Title, content=item.Content, categories=categories_ordenadas
                )
            )

        pagination = Pagination(
            totalRecords=total_results, page=page, pageSize=pageSize, totalPages=total_pages
        )

        if total_results <= 0:
            message.status_code = 204
            message.message = "No se encontraron resultados."

        data = sorted(knowledge_base, key=lambda x: x.id)

        return GetKnowledgeBaseResponse(message=message, data=data, pagination=pagination)
    except Exception as e:
        raise error_response(detail=str(e))


@router.get(path="/GetKnowledgeBaseById", response_model=KnowledgeDataBaseResponse)
async def get_knowledge_data_base(
        id: int = Query(), db: Session = Depends(get_db),
        auth_result: str = Security(auth.verify)) -> KnowledgeDataBaseResponse:
    """
    API GET method to return an unanswered question (by its id).
    \f
    :param id: The id of the question to be retrieved.
    :param db: The current DB instance.
    :return: A NT with the unanswered question.
    """
    message = MessagePost()

    try:
        tabla_media_knowledgecategories = aliased(KnowledgeBaseCategoriesModel)
        result = db.query(KnowledgeDataBaseModel).filter_by(Id=id).first()

        if result is not None:
            # Query to get related categories
            categories = (
                db.query(CategoriesModel)
                .filter(
                    CategoriesModel.Id == tabla_media_knowledgecategories.Category_Id,
                    tabla_media_knowledgecategories.KnowledgeBase_Id == result.Id,
                )
                .all()
            )

            # Creating a list of Category objects
            category_list = [
                Categories(id=category.Id, description=category.Description)
                for category in categories
            ]

            # Creating a KnowledgeDataBaseResponse object
            response = Knowledge(
                id=result.Id,
                title=result.Title,
                content=result.Content,
                categories=category_list,
            )
        else:
            message.message = "No se encontraron resultados."
            message.status_code = 204
            message.errors.append(f"Operacion fallida: No se encontro registro con id {id}.")
            response = {}

        return KnowledgeDataBaseResponse(data=response, message=message)
    except Exception as e:
        raise error_response(detail=str(e))
    raise error_response(detail=f"Knowledge '{id}' not found.")


@router.post(path="/CreateData")
async def create_knowledge_base(
        knowledgeBaseRequest: KnowledgeBaseRequest,
        db: Session = Depends(get_db),
        auth_result: str = Security(auth.verify)
):
    # Crear una instancia de TResponseDataPost
    response = TResponseDataPost()

    added_knowledgebase = None
    added_categories = None
    knowledgebase_categories = KnowledgeBaseCategoriesModel
    question_without_answer = UnansweredQuestionModel
    errors = []  # Lista para almacenar los errores
    have_category = True
    have_question = True
    try:
        response = create_knowledgebase_service(knowledgeBaseRequest, db)
        return response
    except Exception as ex:
        return {"message": "Error en la solicitud."}


@router.put(path="/UpdateData")
async def upload_knowledge_Base(
        knowledgeBaseRequest: UploadKnowledgeBaseRequest,
        db: Session = Depends(get_db),
        auth_result: str = Security(auth.verify)
):
    """
    Uploads the knowledge database.
    \f
    :param knowledgebaseid: The current DB instance.
    :param knowledgeBase: The current DB instance.
    :param db: The current DB instance.
    :return: a Database response based on the current POST status
    """
    try:
        response = update_knowledgebase_service(knowledgeBaseRequest, db)

    except Exception as ex:
        db.rollback()
    return response





@router.delete(
    path="/DeleteData",
)
async def delete_knowledge_data_base(
        id: int = Query(), db: Session = Depends(get_db), auth_result: str = Security(auth.verify)
):
    """
    API DELETE method to delete an knowledge question from the DB.
    \f
    :param id: The id of the knowledge to be deleted.
    :param db: The current DB instance.
    """
    return delete_knowledgebase(id, db)
