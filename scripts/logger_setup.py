import logging


def setup_logger(
    name,
    enable_debug,
):
    # set root logger to warning to stop external DEBUG logs
    logging.getLogger().setLevel(logging.WARNING)

    # create logger
    logger = logging.getLogger(name)

    # remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # set logger level
    if enable_debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # disable propagation to root logger
    logger.propagate = False

    handler = logging.StreamHandler()
    # set up formatted
    formatter = logging.Formatter(
        "# DEBUG: %(name)s"  # DEBUG: module.submodule
        + "\n# "
        + "-" * 30  # -----------------------
        + "\n%(message)s\n"  # output message contents
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    orig_debug = logger.debug

    # wrapper to allow multiple arguments to debug function
    def debug(*args):
        message = " ".join(str(arg) for arg in args)
        orig_debug(message)

    logger.debug = debug

    return logger
