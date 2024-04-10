"""
Main entry point for code-generator.
"""
import logging
import sys
from typing import Optional

import click
import uvicorn

from code_generator import __program_name__, __version__
from code_generator.cli import cli_helper
from code_generator.commons.env_variables import get_env_vars
from code_generator.commons.openai_helper import OpenAIHelper
from code_generator.config_reader.config_reader import ConfigData
from code_generator.generator import generator
from code_generator.service.service import app

# Min OpenAI password length
MIN_PASSWORD_LEN = 5

LOGGER = logging.getLogger(__name__)


@click.group()
@click.version_option(
    prog_name=__program_name__, version=__version__, message="%(prog)s %(version)s"
)
def cli() -> None:
    """
    \b
    CLI to interact with the Code-Generator.
    \f
    :return: None
    """


@cli.command()
def show_credentials() -> None:
    """
    Shows the credentials to be used with OpenAI.
    \f
    :return: None.

    """

    def mask_key(key: str) -> str:
        if len(key) < MIN_PASSWORD_LEN:
            raise ValueError("Invalid OpenIA key length.")
        return ("*" * (len(key) - MIN_PASSWORD_LEN)) + key[-MIN_PASSWORD_LEN:]

    try:
        env_vars = get_env_vars()
        LOGGER.info(f"OpenIA Key      : {mask_key(env_vars.api_key)}")
        LOGGER.info(f"Model           : {env_vars.openai_model}")
        if env_vars.openai_type == "azure":
            LOGGER.info("Credential Type : Azure")
            LOGGER.info(f"> Base          : {env_vars.azure_base}")
            LOGGER.info(f"> Version       : {env_vars.azure_version}")
            LOGGER.info(f"> Deployment Id : {env_vars.azure_deployment_id}")
    except Exception as exc:
        LOGGER.error(f"Error: {exc}")
        sys.exit(1)


@cli.command()
def check_credentials() -> None:
    """
    Checks if OpenAI credentials were configured correctly or not.
    \f
    :return: None.
    """
    try:
        LOGGER.info("Checking credentials...")
        env_vars = get_env_vars()
        helper = OpenAIHelper(env_vars=env_vars)
        response = helper.consume(
            prompt="What is an IA?",
            retries=env_vars.openai_retries,
            retry_sleep_time=env_vars.openai_retry_sleep_time,
        )
        if response:
            LOGGER.info("Credentials worked just fine!")
    except Exception as exc:
        LOGGER.error(f"Error: {exc}")
        sys.exit(1)


@cli.command()
def run_service() -> None:
    """
    Run the code generator as a service to be consumable throw APIRests.
    \f
    :return: None.
    """
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as exc:
        LOGGER.error(f"Something went wrong when running service: {exc}")
        sys.exit(1)


@cli.command()
@cli_helper.config_option
@cli_helper.log_option
@cli_helper.debug_option
@cli_helper.stats_option
@cli_helper.verbose_option
def generate_code(
    config: ConfigData, log: Optional[str], debug: bool, stats: bool, verbose: bool
) -> None:
    """
    Generates code based on the input source architecture using IA.
    \f
    :param config: See click option description.
    :param log: See click option description.
    :param debug: See click option description.
    :param stats: See click option description.
    :param verbose: See click option description.
    :return: None.
    """
    try:
        generator.generate_code(
            config=config,
            env_vars=get_env_vars(),
            log=log,
            debug=debug,
            stats=stats,
            verbose=verbose,
        )
    except Exception as exc:
        LOGGER.error(f"Error: {exc}")
        sys.exit(1)


def main() -> None:
    """
    Main entry point.
    :return: None.
    """
    cli()


if __name__ == "__main__":
    main()
