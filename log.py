import sys


def logger_setup(logger):
    logger.remove()
    logger.add(
        sink='{time:MMM-YYYY}.log',
        format='[+] {time:MMM D, YYYY - HH:mm:ss} | {file} | line: {line} | {level} | {message}\n',
        level='INFO',
        rotation='10 MB',
        compression='zip',
        retention='3 month',
    )
    logger.add(
        sink=sys.stdout,
        format='[+] {time:MMM D, YYYY - HH:mm:ss} | {file} | line: {line} | <level>{level}</level> | {message}\n',
        level='SUCCESS',
    )
