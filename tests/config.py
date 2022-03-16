#!/usr/bin/env python
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Configuration for the bot."""

import os


class DefaultConfig:
    """Bot Configuration"""

    ############## Azure Bot Service ###############
    PORT = 3978
    # APP_ID = os.environ.get("MicrosoftAppId", "") 
    # APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    APP_ID = os.environ.get("MicrosoftAppId", "") 
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")

    ############## LUIS Service ###############
    LUIS_APP_ID = os.environ.get("LuisAppId", "0af71a77-a0d0-4d2e-b63b-e4348b04f146")
    LUIS_API_KEY = os.environ.get("LuisAPIKey", "c0e129a4bd1149088e2e9be2358365e9")
    LUIS_API_HOST_NAME = os.environ.get("LuisAPIHostName", "https://westeurope.api.cognitive.microsoft.com/")

    ############## App Insights Service ###############
    APPINSIGHTS_INSTRUMENTATION_KEY = os.environ.get(
        "AppInsightsInstrumentationKey", "cf71c319-c6e4-4b13-8be6-bf1967fd27d5")
