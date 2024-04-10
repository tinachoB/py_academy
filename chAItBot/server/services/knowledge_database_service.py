import datetime
from typing import List

from pydantic import BaseModel  # Importa BaseModel de pydantic

from server.common.env_variables import get_env_vars
from server.helpers.embeddings_db import EmbeddingsDB
from server.helpers.openai_helper import OpenAIHelper
from server.models.category_database import CategoriesModel
from server.models.knowledge_categories_database import KnowledgeBaseCategoriesModel
from server.models.knowledge_database import KnowledgeDataBaseModel
from server.models.unanswered_question import UnansweredQuestionModel
from server.schemas.knowledge_database import KnowledgeBaseRequest
from server.schemas.wrappers.base_response import MessagePost, TResponseDataPost

__env_vars = get_env_vars()
__openai_helper = OpenAIHelper(config=__env_vars)
__redis_helper = EmbeddingsDB(config=__env_vars.redis)


def create_knowledgebase_service(knowledgeBaseRequest, db):
    message = MessagePost()
    errors = []
    have_category = True
    have_question = True
    response = TResponseDataPost(message=message)
    added_knowledgebase = None

    try:
        # Comprueba si existen categorías
        for item in knowledgeBaseRequest.knowledgeBase.categories:
            existing_category = db.query(CategoriesModel).filter_by(Id=item).first()

            if existing_category is None:
                have_category = False
                response.message.errors.append(
                    f"Operación fallida: Categoría con ID {item} no encontrada."
                )
                response.success = False

        # Si se proporciona un ID de pregunta sin respuesta, comprueba su existencia
        if knowledgeBaseRequest.knowledgeBase.relatedQuestionId is not None:
            question_by_id = (
                db.query(UnansweredQuestionModel)
                .filter_by(id=knowledgeBaseRequest.knowledgeBase.relatedQuestionId)
                .first()
            )

            if question_by_id:
                question_by_id.Resolved = True
                db.commit()
                db.refresh(question_by_id)
            else:
                response.message.errors.append(
                    f"Operación fallida: Pregunta sin respuesta con ID {knowledgeBaseRequest.knowledgeBase.relatedQuestionId} no encontrada."
                )
                response.success = False
                have_question = False

        if not have_category or not have_question:
            response.success = False
            response.message.status_code = 400
            response.message.message = "No se pudo crear correctamente."
        else:
            concatenated_content = f"{knowledgeBaseRequest.knowledgeBase.title}: {knowledgeBaseRequest.knowledgeBase.content}"
            embedding = __openai_helper.encode_text(text=concatenated_content)

            added_knowledgebase = KnowledgeDataBaseModel(
                Title=knowledgeBaseRequest.knowledgeBase.title,
                Content=knowledgeBaseRequest.knowledgeBase.content,
                CreatedOn=datetime.datetime.now(),
                Embedding=embedding.embeddings.tobytes(),
                DocumentId=knowledgeBaseRequest.knowledgeBase.documentId
            )

            db.add(added_knowledgebase)
            db.commit()

            if have_category:
                for item in knowledgeBaseRequest.knowledgeBase.categories:
                    added_categories = KnowledgeBaseCategoriesModel(
                        KnowledgeBase_Id=added_knowledgebase.Id, Category_Id=item
                    )
                    db.add(added_categories)
                db.commit()

                __redis_helper.upload_embedding(
                    embedding.embeddings.tobytes(), added_knowledgebase.Id, concatenated_content,
                    knowledgeBaseRequest.knowledgeBase.categories
                )

            response.message.message = "El registro se creó correctamente."
            response.message.status_code = 201
            response.success = True
            response.message.errors = errors

    except Exception as ex:
        response.message.message = "Operación fallida."
        response.message.status_code = 400
        response.message.errors = errors
        db.rollback()
    finally:
        if added_knowledgebase:
            db.refresh(added_knowledgebase)

    return response


def create_knowledgebase_array_service(request: List[KnowledgeBaseRequest], db):
    message = MessagePost()
    errors = []
    response = TResponseDataPost(message=message)
    added_knowledgebaseArray = []
    added_categoriesArray = []
    categories = request[0].knowledgeBase.categories

    try:
        # Validacion categorias
        if len(categories) > 0:
            for item in categories:
                existing_category = db.query(CategoriesModel).filter_by(Id=item).first()
                if existing_category is None:
                    response.message.errors.append(
                        f"Operación fallida: Categoría con ID {item} no encontrada."
                    )
                    response.success = False
                    return response

        for knowledgeBaseRequest in request:
            concatenated_content = f"{knowledgeBaseRequest.knowledgeBase.title}: {knowledgeBaseRequest.knowledgeBase.content}"
            embedding = __openai_helper.encode_text(text=concatenated_content)

            added_knowledgebase = KnowledgeDataBaseModel(
                Title=knowledgeBaseRequest.knowledgeBase.title,
                Content=knowledgeBaseRequest.knowledgeBase.content,
                CreatedOn=datetime.datetime.now(),
                Embedding=embedding.embeddings.tobytes(),
                DocumentId=knowledgeBaseRequest.knowledgeBase.documentId
            )

            added_knowledgebaseArray.append(added_knowledgebase)

        # No necesitamos validacion aqui ya que esta se la hace dentro del bucle.
        db.add_all(added_knowledgebaseArray)

        db.commit()

        knowledgeBase = (db.query(KnowledgeDataBaseModel).
                         filter(KnowledgeDataBaseModel.DocumentId == request[0].knowledgeBase.documentId).all())

        # Agrego la relacion entre categoria y knowledgeBase
        for item in knowledgeBase:
            concatenated_content = f"{item.Title}: {item.Content}"
            embedding = __openai_helper.encode_text(text=concatenated_content)

            if len(categories) > 1:
                for category in categories:
                    added_categories = KnowledgeBaseCategoriesModel(
                        KnowledgeBase_Id=item.Id, Category_Id=category
                    )
                    added_categoriesArray.append(added_categories)

            else:
                added_categories = KnowledgeBaseCategoriesModel(
                    KnowledgeBase_Id=item.Id, Category_Id=categories[0]
                )
                added_categoriesArray.append(added_categories)

            __redis_helper.upload_embedding(
                embedding.embeddings.tobytes(), item.Id, concatenated_content,
                categories
            )

        db.add_all(added_categoriesArray)
        db.commit()

        response.message.message = "El registro se creó correctamente."
        response.message.status_code = 201
        response.success = True
        response.message.errors = errors

    except Exception as ex:
        response.message.message = "Operación fallida."
        response.message.status_code = 400
        response.message.errors = errors
        db.rollback()

    return response


def delete_categories_from_knowledgebase(idKnowledgebase: int, db):
    categories = (db.query(KnowledgeBaseCategoriesModel).
                  filter(KnowledgeBaseCategoriesModel.KnowledgeBase_Id == idKnowledgebase).all())

    relation_ids_to_delete = [section.Id for section in categories]

    db.query(KnowledgeBaseCategoriesModel).filter(
        KnowledgeBaseCategoriesModel.Id.in_(relation_ids_to_delete)
    ).delete(synchronize_session=False)

    db.commit()


def delete_knowledgebase(id, db):
    response = TResponseDataPost()
    try:
        result = db.query(KnowledgeDataBaseModel).filter_by(Id=id).first()
        if result is not None:
            redis_key = f"doc:{result.Id}"
            __redis_helper.delete_knowledge_entry(redis_key)
            delete_categories_from_knowledgebase(id, db)
            db.delete(result)
            db.commit()
            response.success = True
            response.message.message = "El registro se eliminó correctamente."
        else:
            response.message.errors.append(
                f"Operación fallida: No existe la base de conocimiento con ID {id}."
            )
            response.success = False
            response.message.message = "No existe el registro."
            response.message.status_code = 404
    except Exception as e:
        response.success = False
        response.message.message = "Operacion fallida."

    return response


def update_knowledgebase_service(knowledgeBaseRequest, db):
    knowledgeBaseById = None
    message = MessagePost()
    response = TResponseDataPost(message=message)
    have_category = True
    errors = []

    try:
        knowledgeBaseById = (
            db.query(KnowledgeDataBaseModel)
            .filter_by(Id=knowledgeBaseRequest.knowledgeBase.id)
            .first()
        )

        if knowledgeBaseById:
            for item in knowledgeBaseRequest.knowledgeBase.categories:
                existing_category = (
                    db.query(KnowledgeBaseCategoriesModel).filter_by(Category_Id=item).first()
                )
                if existing_category is None:
                    have_category = False
                    response.message.errors.append(
                        f"Operación fallida: Categoría con ID {item} no encontrada."
                    )
                    response.success = False

            if not have_category:
                response.success = False
                response.message.status_code = 400
                response.message.message = "No se pudo editar correctamente."
            else:
                knowledgeBaseById.Title = knowledgeBaseRequest.knowledgeBase.title
                knowledgeBaseById.Content = knowledgeBaseRequest.knowledgeBase.content

                concatenated_content = f"{knowledgeBaseRequest.knowledgeBase.title}: {knowledgeBaseRequest.knowledgeBase.content}"
                embedding = __openai_helper.encode_text(text=concatenated_content)

                knowledgeBaseById.Embedding = embedding.embeddings.tobytes()
                db.query(KnowledgeBaseCategoriesModel).filter_by(
                    KnowledgeBase_Id=knowledgeBaseRequest.knowledgeBase.id
                ).delete()
                for item in knowledgeBaseRequest.knowledgeBase.categories:
                    updated_categories = KnowledgeBaseCategoriesModel(
                        KnowledgeBase_Id=knowledgeBaseRequest.knowledgeBase.id, Category_Id=item
                    )
                    db.add(updated_categories)
                db.commit()
                db.refresh(knowledgeBaseById)

                __redis_helper.upload_embedding(
                    embedding.embeddings.tobytes(), knowledgeBaseById.Id, concatenated_content,
                    knowledgeBaseRequest.knowledgeBase.categories
                )

                response.message.message = "El registro se actualizó correctamente."
                response.message.status_code = 200
                response.message.errors = errors

        else:
            response.message.message = "No existe el registro."
            response.message.errors.append(
                f"Operación fallida: No existe registro con ID {knowledgeBaseRequest.knowledgeBase.id}."
            )
            response.message.status_code = 404
            response.success = False
    except Exception as ex:
        response.success = False
        response.message.status_code = 400
        response.messages.message = "Operación fallida."
        db.rollback()
    finally:
        if knowledgeBaseById:
            db.refresh(knowledgeBaseById)
    return response
