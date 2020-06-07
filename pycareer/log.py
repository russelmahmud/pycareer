import logging

LOG_LEVEL = logging.getLevelName('DEBUG')
ROOT_LOG_NAME = 'pycareer'
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logs = set()

# For google app engine only
default_handler = logging.getLogger().handlers
if default_handler:
    default_handler[0].setFormatter(formatter)


def get_log_name(name):
    if name == ROOT_LOG_NAME:
        return name
    return ''.join([ROOT_LOG_NAME, '.', name])


def get_logger(name=ROOT_LOG_NAME):
    logger_ = logging.getLogger(get_log_name(name))

    if name not in logs:
        logger_.setLevel(LOG_LEVEL)
        # For stopping double entries of logging in google app engine
        # stream_handler = logging.StreamHandler()
        # stream_handler.setFormatter(formatter)
        # stream_handler.setLevel(LOG_LEVEL)
        # logger_.addHandler(stream_handler)

        logs.add(name)

    return logger_


if __name__ == '__main__':
    tester = get_logger('test_logger')
    tester.error('test 1')
    tester.debug('test 2')
