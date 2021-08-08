import logging
import coloredlogs

fieldstyle = {'asctime': {'color': 'green'},
              'levelname': {'bold': True, 'color': 'white'},
              'filename': {'color': 'cyan'},
              'funcName': {'color': 'blue'},
              'lineno': {'color': 'white'}}

levelstyles = {'critical': {'bold': True, 'color': 'red'},
               'debug': {'color': 'green'},
               'error': {'color': 'red'},
               'info': {'color': 'magenta'},
               'warning': {'color': 'yellow'}}

file = logging.FileHandler("Info.log")
file.setLevel(logging.INFO)
file.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(message)s"))
cric_file = logging.FileHandler("Error.log")

cric_file.setFormatter(
    logging.Formatter("%(asctime)s [%(levelname)s] - [%(filename)s > %(funcName)s() > %(lineno)s] - %(message)s"))
cric_file.setLevel(logging.ERROR)


def getlogger():
    global file, cric_file
    mylogs = logging.getLogger(__name__)
    mylogs.setLevel(logging.DEBUG)

    coloredlogs.install(level=logging.INFO,
                        logger=mylogs,
                        fmt='%(asctime)s [%(levelname)s] - %(message)s',
                        datefmt='%H:%M:%S',
                        field_styles=fieldstyle,
                        level_styles=levelstyles)

    mylogs.addHandler(file)
    mylogs.addHandler(cric_file)
    return mylogs
