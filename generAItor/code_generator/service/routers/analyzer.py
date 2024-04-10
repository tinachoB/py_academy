"""
Generator router methods
"""

import logging
from typing import Annotated

from fastapi import APIRouter, File, UploadFile, status

from code_generator.commons.common import error_detail, error_response
from code_generator.commons.file_helper import analyze_zip_data, unzip_file
from code_generator.service.models.models import CodeGeneratorResponse, Data

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    path="",
    responses={
        status.HTTP_200_OK: {
            "model": CodeGeneratorResponse,
            "description": "The zip file looks good",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Error trying to check the zip file.",
            "content": error_detail(),
        },
    },
)
async def zip_file_check(file: Annotated[UploadFile, File()]) -> CodeGeneratorResponse:
    """
    API POST method to check and validate if the zip file to be used is correctly formed.
    \f
    :param file: The zip file to be checked.
    :return: CodeGeneratorResponse object with the result.
    """
    try:
        LOGGER.debug(f"Incoming ZIP file: {file.filename} - size: {file.size}")
        if analyze_zip_data(unzip_file(file.file)):
            response_data = Data(status=status.HTTP_200_OK, answer="The zip file looks good")
            return CodeGeneratorResponse(data=response_data)
        else:
            LOGGER.error("Invalid zip file content")
            raise error_response(
                detail=f"The {file.filename} does not match with the expected schema.",
                status_code=status.HTTP_412_PRECONDITION_FAILED,
            )
    except Exception as e:
        LOGGER.error(f"Something went wrong trying to open the ZIP file: {file.filename}")
        raise error_response(str(e))
