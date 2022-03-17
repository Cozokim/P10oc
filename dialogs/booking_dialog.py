# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Flight booking dialog."""

from datatypes_date_time.timex import Timex

from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions
from botbuilder.schema import InputHints
from botbuilder.core import MessageFactory, BotTelemetryClient, NullTelemetryClient
from .cancel_and_help_dialog import CancelAndHelpDialog
from .start_date_resolver_dialog import StartDateResolverDialog
from .end_date_resolver_dialog import EndDateResolverDialog


class BookingDialog(CancelAndHelpDialog):
    """Flight booking implementation."""

    # ==== Initialization === #
    def __init__(
        self,
        dialog_id: str = None,
        telemetry_client: BotTelemetryClient = NullTelemetryClient()):

        super(BookingDialog, self).__init__(
            dialog_id or BookingDialog.__name__, telemetry_client)
        self.telemetry_client = telemetry_client

        text_prompt = TextPrompt(TextPrompt.__name__)
        text_prompt.telemetry_client = telemetry_client
        self.add_dialog(text_prompt)

        # Correct Waterfall Dialog with the 5 requested entities
        waterfall_dialog = WaterfallDialog(
            WaterfallDialog.__name__,
            [
                self.origin_step,
                self.destination_step,
                self.start_date_step,
                self.end_date_step,
                self.budget_step,
                self.confirm_step,
                self.final_step,
            ])
        waterfall_dialog.telemetry_client = telemetry_client
        self.add_dialog(waterfall_dialog)
        
        self.initial_dialog_id = WaterfallDialog.__name__
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(StartDateResolverDialog(StartDateResolverDialog.__name__, self.telemetry_client))
        self.add_dialog(EndDateResolverDialog(EndDateResolverDialog.__name__, self.telemetry_client))  

    
    # ==== Origine ==== # 
    async def origin_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt for origin city."""
        
        booking_details = step_context.options

        if booking_details.origin is None:
            msg = "Where do you leave from ?"
            prompt_message = MessageFactory.text(msg, msg, InputHints.expecting_input)
            return await step_context.prompt(TextPrompt.__name__, PromptOptions(prompt=prompt_message))  
        
    
    # ==== Destination ==== # 
    async def destination_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt for destination city."""
        
        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.origin = step_context.result

        if booking_details.destination is None:
            msg = "Where do you want to go?"
            prompt_message = MessageFactory.text(msg, msg, InputHints.expecting_input)
            return await step_context.prompt(TextPrompt.__name__, PromptOptions(prompt=prompt_message))  

        return await step_context.next(booking_details.destination)

    
    # Departure Date 
    async def start_date_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt for departure date.
        This will use the DATE_RESOLVER_DIALOG."""

        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.destination = step_context.result

        if not booking_details.start_date or self.is_ambiguous(booking_details.start_date):
            return await step_context.begin_dialog(StartDateResolverDialog.__name__, booking_details.start_date)  

        return await step_context.next(booking_details.start_date)
    

    # Return Date  
    async def end_date_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt for departure date.
        This will use the DATE_RESOLVER_DIALOG."""

        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.start_date = step_context.result

        if not booking_details.end_date or self.is_ambiguous(booking_details.end_date):
            return await step_context.begin_dialog(EndDateResolverDialog.__name__, booking_details.end_date)  

        return await step_context.next(booking_details.end_date)
    

    #       Budget  
    async def budget_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt for budget."""
        
        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.end_date = step_context.result

        if booking_details.budget is None:
            msg = "What is your budget ? "
            prompt_message = MessageFactory.text(msg, msg, InputHints.expecting_input)
            return await step_context.prompt(TextPrompt.__name__, PromptOptions(prompt=prompt_message))  

        return await step_context.next(booking_details.budget)


    # ==== Confirm ==== # 
    async def confirm_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Confirm the information the user has provided."""
        
        booking_details = step_context.options

        # Capture the results of the previous step's prompt
        booking_details.budget = step_context.result
        
        # boutton yes/no
        msg = (
            f"Are you sure you to book a flight from { booking_details.origin } "
            f"to { booking_details.destination }, "
            f"the { booking_details.start_date} to go back the {booking_details.end_date}, "
            f"for a budget of {booking_details.budget} ? .")
        
        prompt_message = MessageFactory.text(msg, msg, InputHints.expecting_input)
        return await step_context.prompt(ConfirmPrompt.__name__, PromptOptions(prompt=prompt_message))

    
    # Dialogue Final 
    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Complete the interaction, track data, and end the dialog."""

        booking_details = step_context.options

        properties = {}
        properties["origin"] = booking_details.origin
        properties["destination"] = booking_details.destination
        properties["departure_date"] = booking_details.start_date
        properties["return_date"] = booking_details.end_date
        properties["budget"] = booking_details.budget
        
        if step_context.result:
            self.telemetry_client.track_trace("accept", properties, "INFO")
            return await step_context.end_dialog(booking_details)
        
        else:
            sorry_msg = "I'm really sorry that i couldn't help you :( "
            prompt_sorry_msg = MessageFactory.text(sorry_msg, sorry_msg, InputHints.ignoring_input)
            await step_context.context.send_activity(prompt_sorry_msg)

            # Track error
            self.telemetry_client.track_trace("refuse", properties, "ERROR") 

        return await step_context.end_dialog()

    
    def is_ambiguous(self, timex: str) -> bool:
        """Ensure time is correct."""
        
        timex_property = Timex(timex)
        return "definite" not in timex_property.types
