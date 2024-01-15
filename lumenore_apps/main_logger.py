# Copyright © Lumenore Inc. All rights reserved.
# This software is the confidential and proprietary information of
# Lumenore Inc. "Confidential Information".
# You shall * not disclose such Confidential Information and shall use it only in
# accordance with the terms of the intellectual property agreement
# you entered into with Lumenore Inc.
# THIS SOFTWARE IS INTENDED STRICTLY FOR USE BY Lumenore Inc.
# AND ITS PARENT AND/OR SUBSIDIARY COMPANIES. Lumenore
# MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY OF THE SOFTWARE,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR NON-INFRINGEMENT.
# Lumenore SHALL NOT BE LIABLE FOR ANY DAMAGES SUFFERED BY ANY PARTY AS A RESULT
# OF USING, MODIFYING OR DISTRIBUTING THIS SOFTWARE OR ITS DERIVATIVES.

"""main_logger"""

import sys
import logging
import logging.config
from .constants import Constants

constants = Constants()

FORMATTER = logging.Formatter(f"[{constants.get_config('parameters', 'env')}] "
                              f"[%(levelname)s]: [%(asctime)s] [%(lineno)d] [%(filename)s] [%(message)s]")


def get_console_handler():
    """update this doc string"""
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    console_handler.setLevel(logging.INFO)
    return console_handler


def set_up_logging():
    """Set up logging"""
    logger = logging.getLogger(__name__)
    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG)
        logger.addHandler(get_console_handler())
        logger.propagate = False
    return logger
