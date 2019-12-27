import click
import logging
from pprint import pprint

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
@click.option('-v', '--vault', 'vault', default='sops', required=False, multiple=True)
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
    transform = Transforms[format](transform_config, vault_stack)

    logger.info('Transforming')
    result = transform.transform(cfg)
    print(result)

@cli.command()
@click.argument('input', type=click.File('rb'))
def provision(input):
    """Read INPUT and store in the vault service
    """
    logger = logging.getLogger("configs")

    logger.info('Reading config')
    cfg = Config()
    cfg.read(input)

    logger.info('Fetching vault config')
    vault_config = cfg.get_vault_config("aws")

    vault = VaultAws(vault_config)

    logger.info('Storing')
    vault.provision(cfg.get_merged())
