"""
Helper for the CLI.
"""
import logging
from typing import Optional

import click
from click import BadParameter, Context, Parameter

from code_generator.config_reader import config_reader
from code_generator.config_reader.config_reader import ConfigData


def _check_config_file(  # pylint: disable=unused-argument
    ctx: Optional[Context], param: Optional[Parameter], config_file: str
) -> ConfigData:
    """
    Wrapper for exists function in order to make it easy to mock and do not break other
    click functionalities.
    :param config_file: The path to a config file to be validated.
    :return: The config file converted into a dict.
    """
    if config_file is not None:
        return config_reader.get_config(config_file=config_file)
    raise BadParameter("Missing config parameter.")


def _set_debug_mode(  # pylint: disable=unused-argument
    ctx: Optional[Context], param: Optional[Parameter], debug: bool
) -> bool:
    """
    Sets the default log-level.
    :param ctx: The cli content. Not used.
    :param param: The name of the param to be validated. Not used.
    :param debug: The value for the --debug option on the command line.
    :return: True if the --debug option was used, False otherwise.
    """
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    return debug is not None and debug is True


debug_option = click.option(
    "-d",
    "--debug",
    is_flag=True,
    type=click.BOOL,
    default=False,
    callback=_set_debug_mode,
    required=False,
    help="Sets the DEBUG log-level.",
)

verbose_option = click.option(
    "-v",
    "--verbose",
    is_flag=True,
    type=click.BOOL,
    default=False,
    required=False,
    help="Sets the verbosity level.",
)

stats_option = click.option(
    "-s",
    "--stats",
    is_flag=True,
    type=click.BOOL,
    default=False,
    required=False,
    help="Gets stats for the generated code.",
)


log_option = click.option(
    "-l",
    "--log",
    help="Logging will be saved to this file if given.",
    type=click.Path(exists=False, file_okay=True, writable=True, dir_okay=False, resolve_path=True),
    default=None,
    show_default=True,
)


config_option = click.option(
    "-c",
    "--config",
    help="A config file.",
    type=click.Path(exists=True, file_okay=True, writable=True, dir_okay=True, resolve_path=True),
    required=True,
    callback=_check_config_file,
)
