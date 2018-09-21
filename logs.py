###########################################################################
#
#   File Name    Date       Owner                Description
#   ---------   -------    ---------           -----------------------
#   logs.py    7/8/2018  pyflask   Logging module for qzengine 
#
###########################################################################

import logging

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

def info_(prntstr):
    logging.info(prntstr)

def debug_(prntstr):
    logging.debug(prntstr)

