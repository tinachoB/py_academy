import datetime

from sqlalchemy import func

from server.common.env_variables import get_env_vars
from server.helpers.embeddings_db import EmbeddingsDB
from server.helpers.openai_helper import OpenAIHelper
from server.models.category_database import CategoriesModel
from server.schemas.wrappers.base_response import MessagePost, TResponseDataPost

__env_vars = get_env_vars()
__openai_helper = OpenAIHelper(config=__env_vars)
__redis_helper = EmbeddingsDB(config=__env_vars.redis)


def create_category_service(categoryRequest, db):
    message = MessagePost()
    errors = []
    have_category = True
    have_question = True
    response = TResponseDataPost(message=message)
    added_category = None
    existing_category = True
    try:
        existing_category = (
            db.query(CategoriesModel)
            .filter(CategoriesModel.Description.ilike(f"%{categoryRequest.category.description}%"))
            .first()
        )

        if existing_category is not None:
            have_category = False
            response.message.errors.append(
                f"Operación Fallida: Ya existe una categoría con ese nombre."
            )

        if have_category:
            added_category = CategoriesModel(Description=categoryRequest.category.description)
            db.add(added_category)
            db.commit()
            response.message.status_code = 201
            message.message = "La categoría se creó correctamente."
            response.message.errors = errors
        else:
            response.success = False
            response.message.status_code = 409
            response.message.message = "Ya existe una categoría con ese nombre."

    except Exception as ex:
        response.message.message = "No se pudo crear correctamente."
        response.message.status_code = 400
        response.message.errors = errors
        db.rollback()
    finally:
        if added_category:
            db.refresh(added_category)

    return response


def update_category_service(categoryRequest, db):
    message = MessagePost()
    errors = []
    have_category = True
    have_question = True
    message.message = "La categoría se actualizó correctamente."
    response = TResponseDataPost(message=message)
    added_category = None
    existing_category = None
    try:
        categoryById = db.query(CategoriesModel).filter_by(Id=categoryRequest.category.id).first()

        # knowledgeBaseById = db.query(KnowledgeDataBaseModel).filter_by(Id=knowledgeBaseRequest.knowledgeBase.id).first()
        # knowledgeBaseById.Title = knowledgeBaseRequest.knowledgeBase.title

        existing_category = (
            db.query(CategoriesModel)
            .filter(
                func.lower(CategoriesModel.Description) == func.lower(categoryRequest.category.description),
                CategoriesModel.Id != categoryRequest.category.id
            )
            .first()
        )

        if categoryById is None:
            have_category = False
            response.success = False
            response.message.status_code = 404
            response.message.message = "No existe el registro."
            response.message.errors.append(
                f"Operación Fallida: No existe categoría con ID {categoryRequest.category.id}"
            )
        else:
            if existing_category is not None:
                response.success = False
                response.message.status_code = 409
                response.message.message = "Ya existe una categoría con ese nombre."
                have_category = False

        if have_category:
            categoryById.Description = categoryRequest.category.description
            db.commit()
            db.refresh(categoryById)
            response.message.errors = errors

    except Exception as ex:
        response.message.message = "Operación fallida."
        response.message.status_code = 500
        response.message.errors = errors
        db.rollback()
    finally:
        if have_category:
            db.refresh(categoryById)

    return response
