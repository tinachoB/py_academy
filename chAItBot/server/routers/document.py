import base64
import re
from datetime import datetime
from http.client import HTTPException
from typing import Optional

from fastapi import APIRouter, File, UploadFile, Body, Query
from docx import Document
from fastapi.responses import JSONResponse
from io import BytesIO
from fastapi.params import Depends
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from server.common.common import error_detail, error_response
from server.common.env_variables import get_env_vars
from server.helpers.embeddings_db import EmbeddingsDB
from server.helpers.mysql_helper import get_db
from server.helpers.openai_helper import OpenAIHelper
from server.models.category_database import CategoriesModel
from server.models.document import DocumentModel
from server.models.documentrelateddata import DocumentRelatedDataModel
from server.models.knowledge_database import KnowledgeDataBaseModel
from server.routers.knowledge_database import delete_knowledge_data_base
from server.schemas.category_database import (
    Category,
    CategoryBaseByIdRequest,
    CategoryBaseRequest,
    CategoryResponse,
    Pagination, GetCategoryById,
)
from server.schemas.document import document_request, document_with_errorsSchema, document_response, document_save_data
from server.schemas.knowledge_database import KnowledgeBaseRequest, KnowledgeBase
from server.schemas.wrappers.base_response import MessagePost, TResponseDataPost, TResponseDataGet
from server.services.category_service import create_category_service, update_category_service
from server.services.knowledge_database_service import create_knowledgebase_service, create_knowledgebase_array_service, \
    delete_knowledgebase

router = APIRouter()

__env_vars = get_env_vars()
__openai_helper = OpenAIHelper(config=__env_vars)
__redis_helper = EmbeddingsDB(config=__env_vars.redis)


# __unanswered_questions = UnansweredQuestionsDB(config=get_env_vars().redis)

def decode_base64(encoded_data):
    try:
        decoded_data = base64.b64decode(encoded_data)
        return decoded_data
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error decoding Base64: " + str(e))


def extract_sections(file_content, start_style_name, end_style_name):
    document = Document(BytesIO(file_content))
    sections = []
    current_section = {"title": "", "content": []}

    for paragraph in document.paragraphs:
        if paragraph.style.name.startswith(start_style_name):
            # Comenzamos una nueva sección
            if current_section["title"]:
                sections.append(current_section.copy())  # Guardar la sección anterior
                current_section = {"title": "", "content": []}  # Reiniciar la sección actual
            current_section["title"] = paragraph.text
        elif paragraph.style.name.startswith(end_style_name):
            # Finalizamos la sección actual
            sections.append(current_section.copy())
            current_section = {"title": "", "content": []}  # Reiniciar la sección actual
        elif current_section["title"]:
            # Estamos dentro de una sección, agregamos el contenido
            asd = paragraph.style.name
            if paragraph.style.name.startswith('List'):
                # Detectar listas y agregar elementos como HTML
                list_html = "<li>"
                for run in paragraph.runs:
                    if run.text.strip():  # Ignorar elementos de lista vacíos
                        list_html += f"{run.text}"
                list_html += "</li>"
                list_html = list_html.replace("\n", "<br/>")
                current_section["content"].append(list_html)
            else:
                # No es una lista, agregar el párrafo completo
                current_section["content"].append(paragraph.text)
                # sections.append(current_section.copy())
                # current_section = {"title": current_section["title"], "content": []}  # reinicio contenido

    # Asegurarnos de agregar la última sección si existe
    if current_section["title"]:
        sections.append(current_section)

    return sections


def parse_sections(sections: []) -> []:
    response = []
    for section in sections:
        # Convierte la lista de strings en una sola cadena usando "<br/>" como separador
        section_content_as_string = None
        if len(section["content"]) == 1 and section["content"][0] != "" and section["content"][0].isspace() is False:
            section_content_as_string = "<br/>".join(section["content"])
        elif len(section["content"]) > 1:
            section_content_as_string = "<br/>".join(section["content"])
        if section_content_as_string:
            # Asigna la cadena resultante de nuevo a section["content"]
            response.append({"title": section["title"], "content": section_content_as_string})

    return response


def create_request_document_related_data(sections: [], existing_elements: [], existing_elements_in_docrelated: [],
                                         db: Session = Depends(get_db)) -> {}:
    # existing_elements = filter(lambda x: x.Status != 2, existing_elements)
    requests = []
    sections_with_errors = []  # Se almacena las secciones con errores
    for section in sections:
        if (len(section["content"]) > 0
                and section["content"] not in [title.Content for title in existing_elements]
                and section["content"] not in [title.Content for title in existing_elements_in_docrelated]):
            if (len(section["content"]) + len(section["title"])) <= 768:
                request = DocumentRelatedDataModel(
                    Title=section["title"],
                    Content=section["content"],
                    DocumentId=id_document,
                    Status=1  # Todo bien paso correctamente
                )
                requests.append(request)
            else:
                request = DocumentRelatedDataModel(
                    Title=section["title"],
                    Content=section["content"],
                    DocumentId=id_document,
                    Status=0  # Superó el límite de caracteres
                )
                requests.append(request)
                sections_with_errors.append(section)
        elif len(section["content"]) > 0:

            objeto_encontrado = next((objeto for objeto in existing_elements_in_docrelated
                                      if (objeto.Title == section["title"]
                                          and objeto.Status == 2
                                          and objeto.Id == id_document)), None)

            if objeto_encontrado is None:
                request = DocumentRelatedDataModel(
                    Title=section["title"],
                    Content=section["content"],
                    DocumentId=id_document,
                    Status=2  # Duplicado
                )
                requests.append(request)
                sections_with_errors.append(section)

    return {"requests": requests, "sections_with_errors": sections_with_errors}


@router.post(path="/ReadDocument")
async def create_category(document: document_request, db: Session = Depends(get_db)):
    global id_document
    response = TResponseDataGet
    try:
        file_content = decode_base64(document.file)

        # Aqui almacenamos el archivo analizado.
        sections = extract_sections(file_content, "Heading", "Heading")
        section_parsed = parse_sections(sections)  # Archivo parseado y ajustado
        cant_sections = len(section_parsed)
        id_document = None  # Aqui almaceno el Id del archivo creado.
        # Validaciones
        if cant_sections > 0:
            validation = lambda obj: or_(func.lower(obj.Name) == document.name.lower(),
                                         func.lower(obj.FileName) == document.filename.lower())
            # Ajustar validacion Listobich
            document_exist = (db.query(DocumentModel).filter(validation(DocumentModel)).first())

            if (document_exist):
                # Retornar error de validacion
                return False
            else:
                request = DocumentModel(
                    Name=document.name,
                    Description=document.description,
                    UploadDate=datetime.now()
                )
                # Guardo el archivo y obtengo Id.
                db.add(request)
                db.commit()
                id_document = request.Id

        if id_document:
            existing_elements = db.query(KnowledgeDataBaseModel).filter(
                KnowledgeDataBaseModel.Title.in_([section["title"] for section in section_parsed]),
                KnowledgeDataBaseModel.Content.in_([section["content"] for section in section_parsed])
            ).all()

            existing_elements_in_docrelated = db.query(DocumentRelatedDataModel).filter(
                DocumentRelatedDataModel.Title.in_([section["title"] for section in section_parsed]),
                DocumentRelatedDataModel.Content.in_([section["content"] for section in section_parsed])
            ).all()
            all_requests = create_request_document_related_data(section_parsed, existing_elements,
                                                                existing_elements_in_docrelated, db)

            # Guardo cambios en base de datos
            db.add_all(all_requests["requests"])
            db.commit()

        data = document_response(documentId=id_document)
        response = TResponseDataGet(data=data)

        return response
    except Exception as ex:
        db.rollback()
        return response


@router.post(path="/SaveDocumentData")
async def save_document_related_data(request: document_save_data, db: Session = Depends(get_db)):
    # Logica de aplicacion

    message = MessagePost()
    response = TResponseDataPost(message=message)
    try:
        # Paso 1 de la ED. Leer datos existentes del documento
        sections = db.query(DocumentRelatedDataModel).filter(DocumentRelatedDataModel.DocumentId == request.id,
                                                             DocumentRelatedDataModel.Status == 1).all()

        if len(sections) == 0:
            response.message.message = "No se encontró ese regístro"
            response.message.status_code = 404
            response.message.errors = []
            return response

        knowledgeBase_request_array = [KnowledgeBaseRequest(
            knowledgeBase=KnowledgeBase(title=section.Title,
                                        content=section.Content,
                                        categories=request.categories,
                                        documentId=request.id)) for section in sections]

        # Paso 2 de la ED. Insertar datos del documento en la base de conocimiento
        response = create_knowledgebase_array_service(knowledgeBase_request_array, db)

        # Paso 3 de la ED. Eliminar datos de la tabla intermedia
        if response.message.status_code == 201:
            sections = (db.query(DocumentRelatedDataModel).
                        filter(DocumentRelatedDataModel.DocumentId == request.id).all())
            section_ids_to_delete = [section.Id for section in sections]

            db.query(DocumentRelatedDataModel).filter(
                DocumentRelatedDataModel.Id.in_(section_ids_to_delete)
            ).delete(synchronize_session=False)
            db.commit()

    except Exception as ex:
        response.message.message = "Operación fallida."
        response.message.status_code = 400
        response.message.errors = []
        db.rollback()

    return response

@router.post(path="/DeleteDocument")
async def delete_document(id: int = Query(), db: Session = Depends(get_db)):
    # Logica de aplicacion

    message = MessagePost()
    response = TResponseDataPost(message=message)
    try:
        # Paso 1 de la ED.
        knowledgeBaseAll = db.query(KnowledgeDataBaseModel).filter(KnowledgeDataBaseModel.DocumentId == id).all()

        if len(knowledgeBaseAll) == 0:
            response.message.message = "No se encontró ese regístro."
            response.message.status_code = 404
            response.message.errors = []
            return response

        knowledgeBaseIds = [conocimiento.Id for conocimiento in knowledgeBaseAll]

        # Paso 2 de la ED.
        for idknow in knowledgeBaseIds:
            response = delete_knowledgebase(idknow, db)

        # Paso 3 de la ED.
        if response.message.status_code == 200:
            db.query(DocumentModel).filter(DocumentModel.Id == id).delete(synchronize_session=False)
            db.commit()

    except Exception as ex:
        response.message.message = "Operación fallida."
        response.message.status_code = 400
        response.message.errors = []
        db.rollback()

    return response