"""
Generation code stuff.
"""
import logging
import os
from pathlib import Path
from typing import List, Optional

from code_generator.commons import file_helper
from code_generator.commons.code_stats import CodeStatsCounter
from code_generator.commons.elapsed_time import ElapsedTime
from code_generator.commons.env_variables import EnvVars
from code_generator.commons.logger_helper import initialize_logger
from code_generator.commons.openai_helper import OpenAIHelper
from code_generator.config_reader.config_reader import ConfigData
from code_generator.config_reader.types import FileTag, Paths, Target, ValueTag
from code_generator.generator.types import TargetData

LOGGER = logging.getLogger(__name__)


def _get_target_data(target: Target, paths: Paths) -> Optional[TargetData]:
    """
    Gets the information from a target configured on the config file
    and creates a target data.

    :param target:
    :return: A NT with the data needed to create a target.
    """
    try:
        output_file = file_helper.format_file_path(file=target.output, paths=paths)

        prompt = file_helper.get_file_content(file=target.prompt.file, paths=paths)
        for tag in target.prompt.tags:
            if isinstance(tag, FileTag):
                file_content = file_helper.get_file_content(file=tag.file, paths=paths)
                prompt = prompt.replace(tag.tag, file_content)
            if isinstance(tag, ValueTag):
                prompt = prompt.replace(tag.tag, tag.value)

        return TargetData(output_file=output_file, prompt=prompt)
    except Exception as e:
        LOGGER.error(f"Error trying to get target data. Error: {e} - Skipping target...")
    return None


def _create_target_file(file_path: str, content: str) -> bool:
    """
    Creates a file and stores the content on it.

    :param file_path: The path of the file to be created.
    :param content: The content of the file.
    :return: True if the target was generated successfully, False otherwise.
    """
    try:
        # Create the output dir, just in case.
        os.makedirs(Path(file_path).parent, exist_ok=True)

        # Write the file content.
        with open(file_path, "wt", encoding="utf-8") as file:
            file.write(content)
            return True

    except Exception as e:
        LOGGER.error(f"Error creating target file. Error: {e}")
    return False


def _generate_target(
    target: TargetData, chat_assistant: OpenAIHelper, retries: int, retry_sleep_time: int
) -> bool:
    """
    Generates a target by calling OpenIA chat completion and storing
    the result into a fie.

    :param target: An NT with the info needed to create the target.
    :param chat_assistant: A helper to use OpenIA.
    :param retries: The number of retries in case of error.
    :param retry_sleep_time: The time to wait until the next try.
    :return: True if the target was generated successfully, False otherwise.
    """
    LOGGER.debug("Using Chat-GPT to generate the target...")
    response = chat_assistant.consume(
        prompt=target.prompt, retries=retries, retry_sleep_time=retry_sleep_time
    )
    if response is not None:
        LOGGER.debug(f"Generating the target file {Path(target.output_file).name}")
        return _create_target_file(file_path=target.output_file, content=response)
    return False


def generate_code(  # pylint: disable=too-many-arguments,too-many-locals,too-many-statements
    config: ConfigData,
    env_vars: EnvVars,
    log: Optional[str] = None,
    debug: bool = False,
    stats: bool = False,
    verbose: bool = False,
) -> None:
    """
    Generates code based on the configuration file.

    :param config: The config.
    :param env_vars: The environment variables.
    :param log: The name of the log file.
    :param debug: Flag for debug mode.
    :param stats: Flag to generate stats.
    :param verbose: Flag for verbosity mode.
    :return: None.
    """
    initialize_logger(log=log)

    LOGGER.debug("Starting generating code...")
    LOGGER.info(f"Targets to generate: {len([t for t in config.targets if t.generate])}")

    elapsed_time = ElapsedTime()

    LOGGER.debug(f"Start-Time: {elapsed_time.start()}")

    chat_assistant = OpenAIHelper(env_vars=env_vars)
    code_stats = CodeStatsCounter()
    generated_targets: List[str] = []

    for i, target in enumerate(config.targets):
        if target.generate:
            LOGGER.info(f"Generating target {i + 1}/{len(config.targets)}")
        else:
            LOGGER.info(f"Skipping target {i + 1}/{len(config.targets)}")
            continue

        target_filename = file_helper.format_file_path(file=target.output, paths=config.paths)
        LOGGER.info(f"Target: {target_filename}")
        target_data = _get_target_data(target=target, paths=config.paths)
        if target_data is not None:

            if verbose:
                LOGGER.info(f"Generated prompt:\n{target_data.prompt}")

            generated_target = _generate_target(
                target=target_data,
                chat_assistant=chat_assistant,
                retries=env_vars.openai_retries,
                retry_sleep_time=env_vars.openai_retry_sleep_time,
            )

            if generated_target:
                generated_targets.append(target_filename)
                if stats:
                    LOGGER.debug(f"Getting code stats for {Path(target_data.output_file).name}...")
                    code_stats.get_stats(file=target_data.output_file)
                    LOGGER.debug("Done.")

    if generated_targets:
        LOGGER.info("")
        LOGGER.info(
            f"Generated Targets Summary using model: '{env_vars.openai_model}' and "
            f"api_version: '{env_vars.azure_version}'"
        )
        for i, target_output in enumerate(generated_targets):
            LOGGER.info(f"  [{i + 1:>2}/{len(generated_targets):<2}] {target_output}")

        if stats:
            if not code_stats.is_frozen_windows():
                LOGGER.info("")
                LOGGER.info("Code Stats")
                LOGGER.info(f"  Code lines count   : {code_stats.stats.code_lines_count}")
                LOGGER.info(f"  Comment lines count: {code_stats.stats.comments_lines_count}")
                LOGGER.info(f"  Empty lines count  : {code_stats.stats.empty_lines_count}")
            LOGGER.info("")
            LOGGER.info("OpenAI Stats")
            LOGGER.info(f"  Prompt    : {chat_assistant.stats.prompt_tokens}")
            LOGGER.info(f"  Completion: {chat_assistant.stats.completion_tokens}")
            LOGGER.info(f"  Total     : {chat_assistant.stats.total_tokens}")
            LOGGER.info("")
            LOGGER.info("OpenAI Pricing:")
            input_charges = (
                chat_assistant.stats.prompt_tokens * env_vars.openai_input_price / 1000.0
            )
            output_charges = (
                chat_assistant.stats.completion_tokens * env_vars.openai_output_price / 1000.0
            )
            LOGGER.info(f"  Input Charges : USD {input_charges:.4f}")
            LOGGER.info(f"  Output Charges: USD {output_charges:.4f}")
            LOGGER.info(f"  Total Charges : USD {input_charges + output_charges:.4f}")

    LOGGER.info("")
    LOGGER.debug(f"End-Time: {elapsed_time.end()}")
    LOGGER.debug(f"Time-Elapsed: {elapsed_time.elapsed}")
    LOGGER.info("Done.")
