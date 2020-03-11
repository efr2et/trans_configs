import click
import logging
from pprint import pprint

from . import __version__

from .config import Config
from .transform import Transforms
from .vault import Vaults
from .vault import Stack as VaultStack

@click.group()
def cli():
    """
    Tool for working with YAML-formatted config generation. Or something.
    """
    pass

@cli.command()
@click.argument('input', type=click.File('rb'))
@click.argument('format')
@click.argument('output', type=click.File('wb'))
@click.option('-v', '--vault', 'vault', default=['sops'], required=False, multiple=True)
def transform(input, format, output, vault):
    """Transform INPUT into FORMAT format and output to OUTPUT
    """
    logger = logging.getLogger("configs")

    logger.info('Reading input config')
    cfg = Config()
    cfg.read(input)

    logger.info('Initializing vaults')
    vaults = []
    for vault_name in vault:
        logger.debug(vault_name)
        vault_config = cfg.get_vault_config(vault_name)
        vault_obj = Vaults[vault_name](vault_config)
        vaults.append(vault_obj)

    vault_stack = VaultStack(vaults)

    logger.info('Initializing transform')
    transform_config = cfg.get_transform_config(format)
    transform = Transforms[format](transform_config)

    logger.info('Transforming')
    result = transform.transform(cfg, vault_stack)
    print(result)

@cli.command()
@click.argument('input', type=click.File('rb'))
@click.argument('source_vault')
@click.argument('target_vault')
def provision(input, source_vault, target_vault):
    """Read INPUT and store in the vault service
    """
    logger = logging.getLogger("configs")

    logger.info('Reading config')
    cfg = Config()
    cfg.read(input)

    logger.info('Initializing source vault')
    source_vault_config = cfg.get_vault_config(source_vault)
    source_vault = Vaults[source_vault](source_vault_config)

    logger.info('Initializing target valut')
    target_vault_config = cfg.get_vault_config(target_vault)
    target_vault = Vaults[target_vault](target_vault_config)

    logger.info('Fetching config data')
    secrets = cfg.get_merged(source_vault)

    logger.info('Provisioning in target vault')
    target_vault.provision(secrets)

@cli.command()
def version():
    """Display the program version
    """
    print(__version__)

