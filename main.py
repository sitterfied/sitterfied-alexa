# -*- coding: utf-8 -*-
from skills import SitterfiedSkill


def lambda_handler(event, context):
    '''
    Main entry point for the Lambda function.

    '''
    return SitterfiedSkill().execute(event, context)
