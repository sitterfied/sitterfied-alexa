# -*- coding: utf-8 -*-
import logging

from skills import SitterfiedSkill

logger = logging.getLogger(__name__)


def lambda_handler(event, context):
    '''
    Main entry point for the Lambda function.

    '''
    return SitterfiedSkill().execute(event, context)
