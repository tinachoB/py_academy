"""
Generator router methods
"""
import io
import logging
import os
import shutil
import tempfile
import zipfile
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse

from code_generator.commons.common import error_response
from code_generator.commons.env_variables import get_env_vars
from code_generator.commons.file_helper import analyze_zip_data, unzip_file
from code_generator.config_reader import config_reader
from code_generator.generator import generator

LOGGER = logging.getLogger(__name__)

router = APIRouter()

TEMP_DIR = "tmp/"


def _extract_content_from(upload_file: Annotated[UploadFile, File()]) -> str:
    """
    Unzip the file being passed as parameter and return its content
    :param upload_file: Zip file to extract information from.
    :return: Path where the content was downloaded.
    """
    try:
        # Create a temporary directory for extraction (it will be deleted at the end of the execution)
        os.makedirs(TEMP_DIR, exist_ok=True)

        LOGGER.info(f"Downloading and extracting information from {upload_file.filename} file")

        # Save the uploaded ZIP file locally
        file_path = os.path.join(TEMP_DIR, upload_file.filename)
        with open(file_path, "wb") as file_object:
            upload_file.file.seek(0)  # Reset the file position to the beginning
            file_object.write(upload_file.file.read())

        # Unzip the file under the expected TMP_DIR directory
        unzip_dir = os.path.join(TEMP_DIR, upload_file.filename.split(".")[0])
        with zipfile.ZipFile(file_path, "r") as zip_ref:
            zip_ref.extractall(unzip_dir)

        return unzip_dir

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during extraction: {str(e)}",
        )


def _call_generator(directory: str) -> None:
    """
    Calls the generator method to start producing output data from Azure OpenAi
    :param directory: Directory path where all needed files to call generator are.
    return None.
    """
    try:
        # Get the config file from the zip extracted previously and call the generator method
        config_file = config_reader.get_config(config_file=os.path.join(directory, "config.json"))
        generator.generate_code(config=config_file, env_vars=get_env_vars())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calling OpenAI Generator: {str(e)}",
        )


def _build_streaming_response(output_path: str) -> StreamingResponse:
    """
    Builds the streaming response (output zip) with the results of the Azure OpenAI call.
    :param output_path: Path to the resulting Azure OpenAI files being generated.
    :return: The Output zip file built as a StreamingResponse object managed by FastAPI.
    """
    try:
        output_files_content = []
        for file in os.listdir(output_path):
            output_files_content.append(os.path.join(output_path, file))

        # BytesIO buffer to store the ZIP file
        buffer = io.BytesIO()
        # Creates a ZipFile object
        with zipfile.ZipFile(buffer, "w") as zip_output:
            # Adds each resulting OpenAI calling results into the output zip
            for file in output_files_content:
                zip_output.write(file)

        # Move the buffer position to the beginning
        buffer.seek(0)

        # Set the response headers
        headers = {
            "Content-Disposition": "attachment; filename=result_files.zip",
            "Content-Type": "application/zip",
        }

        return StreamingResponse(iter([buffer.getvalue()]), headers=headers)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error while trying to build the StreamingResponse object: {str(e)}",
        )


@router.post(path="")
async def generate_code(file: Annotated[UploadFile, File()]) -> StreamingResponse:
    """
    API POST method to interact with Azure OpenAI and return the specific output
    based on the input parameter.
    \f
    :param file: The zip file to be checked.
    :return: CodeGeneratorResponse object with the result.
    """
    try:
        LOGGER.debug(f"Incoming ZIP file: {file.filename} - size: {file.size}")
        if analyze_zip_data(unzip_file(file.file)):
            # Extract the contents of the uploaded ZIP file
            extracted_dir: str = _extract_content_from(file)

            LOGGER.info(f"Files unzipped in: {extracted_dir} folder. Calling generator...")

            _call_generator(directory=extracted_dir)

            LOGGER.info(
                f"Output files generated: {os.listdir(os.path.join(extracted_dir, 'output'))}"
            )

            return _build_streaming_response(output_path=os.path.join(extracted_dir, "output"))
        else:
            LOGGER.error("Invalid zip file content")
            raise error_response(
                detail=f"The {file.filename} does not match with the expected schema.",
                status_code=status.HTTP_412_PRECONDITION_FAILED,
            )
    except Exception as e:
        LOGGER.error(f"Something went wrong trying to open the ZIP file: {file.filename}")
        raise error_response(str(e))
    finally:
        # Remove the temporary directory and its contents
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
