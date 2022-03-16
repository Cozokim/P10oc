#!/usr/bin/env python
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Configuration for the bot."""

import os


class DefaultConfig:
    """Bot Configuration"""

    ############## Azure Bot Service ###############
    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "") 
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")

    ############## LUIS Service ###############
    LUIS_APP_ID = os.environ.get("LuisAppId", "")
    LUIS_API_KEY = os.environ.get("LuisAPIKey", "")
    LUIS_API_HOST_NAME = os.environ.get("LuisAPIHostName", "")

    ############## App Insights Service ###############
    APPINSIGHTS_INSTRUMENTATION_KEY = os.environ.get(
        "AppInsightsInstrumentationKey", "")
