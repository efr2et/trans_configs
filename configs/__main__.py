import logging

if __name__ == "__main__":
    from .cli import cli
    # Set up logging
    logger = logging.getLogger("configs")
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
            '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    cli()

