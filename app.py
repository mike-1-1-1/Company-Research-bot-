#TODO: fix Exception caught : [Errno 54] Connection reset by peer
#TODO: add more targeted exception handling.
#TODO: add integration testing

# app.py
from dotenv import load_dotenv
from microsoft_agents.hosting.core import (
   AgentApplication,
   TurnState,
   TurnContext,
   MemoryStorage,
   ConversationState
)
from microsoft_agents.hosting.aiohttp import CloudAdapter
from agent_core.company_research_agent import CompanyResearchAgent
from start_server import start_server

import os

from collections.abc import Awaitable, Callable

from microsoft_agents.activity import Activity, ActivityTypes, SuggestedActions, CardAction

import copy

import asyncio

from bot_logging import Logger 

def generate_selection_menu() -> Activity:
    """
    Generates an interactive selection menu with suggested actions for the user.
    """
    activity = Activity(
        type=ActivityTypes.message,
        text="Welcome! Please choose the workflow action you would like to run today:"
    )
    
    # Build interactive quick-reply buttons
    activity.suggested_actions = SuggestedActions(
        actions=[
            CardAction(title="📊 Data Collection", type="imBack", value="Data Collection"),
            CardAction(title="📈 Data Analysis", type="imBack", value="Data Analysis"),
            CardAction(title="📋 Report Generation", type="imBack", value="Report Generation")
        ]
    )
    
    return activity

def generate_analysis_type_menu() -> Activity:
    """
    Generates an interactive selection menu for data analysis types.
    """
    activity = Activity(
        type=ActivityTypes.message,
        text="Please choose the type of data analysis you would like to perform:"
    )
    
    # Build interactive quick-reply buttons
    activity.suggested_actions = SuggestedActions(
        actions=[
            CardAction(title="📊 Comparison", type="imBack", value="Comparison Analysis"),
            CardAction(title="📈 Trend", type="imBack", value="Trend Analysis"),
            CardAction(title="📋 Summary", type="imBack", value="Summary Analysis")
        ]
    )
    
    return activity

def generate_format_selection_menu() -> Activity:
    """
    Generates an interactive selection menu for report generation formats.
    """
    activity = Activity(
        type=ActivityTypes.message,
        text="Please choose the format for your report generation:"
    )
    
    # Build interactive quick-reply buttons
    activity.suggested_actions = SuggestedActions(
        actions=[
            CardAction(title="📄 Short summary", type="imBack", value="Short summary"),
            CardAction(title="📝 Full report", type="imBack", value="Full report"),
        ]
    )
    
    return activity

def generate_delivery_method_menu() -> Activity:
    """
    Generates an interactive selection menu for report delivery methods.
    """
    activity = Activity(
        type=ActivityTypes.message,
        text="Please choose the delivery method for your report:"
    )
    
    # Build interactive quick-reply buttons
    activity.suggested_actions = SuggestedActions(
        actions=[
            CardAction(title="📧 Email", type="imBack", value="Email"),
            CardAction(title="🖥️ Display", type="imBack", value="Display"),
        ]
    )
    
    return activity

storage = MemoryStorage()

conversation_state = ConversationState(storage)

user_action_accessor = conversation_state.create_property("user_action")

data_collection_accessor = conversation_state.create_property("data_collection_accessor")
data_analysis_accessor = conversation_state.create_property("data_analysis_accessor")
data_report_accessor = conversation_state.create_property("data_report_accessor")

default_user_action = {"user_action": None}

default_data_collection_info = {"step": "ask company name", "history": {}, "ai_responses": [], "step_count" : 0}
default_data_analysis_info = {"step": "ask analysis type", "history": {}, "ai_responses": [], "step_count" : 0}
default_data_report_info = {"step": "ask report style", "history": {}, "ai_responses": [], "step_count" : 0}

max_data_collection_responses_stored = 3
max_data_analysis_responses_stored = 3
max_data_report_responses_stored = 3

load_dotenv()
try:
    agent_core = CompanyResearchAgent(name="CompanyCoreResearchAgent", config={"OPEN_AI_API_KEY": os.getenv("OPEN_AI_API_KEY")})
except Exception as e:
    Logger.error(f"❌ Failed to initialize CompanyResearchAgent: {e}")
    raise e
agent_core
class InputInterceptorMiddleware:
    async def on_turn(
        self, 
        turn_context: TurnContext, 
        next_turn: Callable[[], Awaitable[None]]
    ):
        #print('intercept_every_input', turn_context.activity.type, turn_context.activity.text)

        await conversation_state.load(turn_context)

        user_action = await user_action_accessor.get(turn_context, default_value_or_factory=lambda: copy.deepcopy(default_user_action))

        # Only intercept if the incoming activity is an actual user text message

        if turn_context.activity.type == "message" and turn_context.activity.text:
            user_raw_input = turn_context.activity.text.lower().strip() if turn_context.activity.text else ""
            Logger.info(f"[APPLICATION INTERCEPTED]: {user_raw_input}, action: {user_action['user_action']}")

            if(user_raw_input):
                # Example: Validate user input length for Data Collection workflow
                if len(user_raw_input) < 2 or len(user_raw_input) > 100:
                    await turn_context.send_activity("Input must be between 2 and 100 characters. Please try again.")
                    return # Stops execution entirely; never calls next_turn()

            if(user_action['user_action'] == "Data Collection"):
                data_collection_info = await data_collection_accessor.get(turn_context, default_value_or_factory=lambda: copy.deepcopy(default_data_collection_info))
                if(data_collection_info["step"] == "ask company name"):
                    try:
                        if not agent_core.does_company_name_probably_exist(user_raw_input):
                            await turn_context.send_activity(f"The company name '{user_raw_input}' does not seem to exist. Please enter a valid company name.")
                            return # Stops execution entirely; never calls next_turn()
                    except Exception as e:
                        Logger.error(f"Error validating company name: {e}")
                        await turn_context.send_activity(f"Error validating company name. Please try again.")
                        return # Stops execution entirely; never calls next_turn()
                elif(data_collection_info["step"] == "ask company topic"):
                    #no validation for now, but could validate if the topic is relevant to the company
                    pass
                elif(data_collection_info["step"] == "ask timeframe"):
                    try: 
                        if not agent_core.is_time_frame_valid(user_raw_input):
                            await turn_context.send_activity(f"The time frame '{user_raw_input}' is not valid. Please enter a valid time frame. (such as 'last 5 years', 'Q1 2023', etc.)")
                        return # Stops execution entirely; never calls next_turn()
                    except Exception as e:
                        Logger.error(f"Error validating time frame: {e}")
                        await turn_context.send_activity(f"Error validating time frame. Please try again.")
                        return # Stops execution entirely; never calls next_turn()
            elif(user_action['user_action'] == "Data Analysis"):
                data_analysis_info = await data_analysis_accessor.get(turn_context, default_value_or_factory=lambda: copy.deepcopy(default_data_analysis_info))
                if(data_analysis_info["step"] == "ask analysis type"):
                    #Could actually validate with ai so that the input doesn't need to be gramatically perfect, but for now just check if the input is perfectly one of the three options
                    if(not(("comparison" in user_raw_input) ^ ("trend" in user_raw_input) ^ ("summary" in user_raw_input))):
                        await turn_context.send_activity("Invalid analysis type. Please choose from the provided options.")
                        await turn_context.send_activity(generate_analysis_type_menu())
                        return # Stops execution entirely; never calls next_turn()
            elif(user_action['user_action'] == "Report Generation"):
                data_report_info = await data_report_accessor.get(turn_context, default_value_or_factory=lambda: copy.deepcopy(default_data_report_info))
                if(data_report_info["step"] == "ask report style"):
                    #Could actually validate with ai so that the input doesn't need to be gramatically perfect, but for now just check if the input is perfectly one of the two options
                    if(not(("short" in user_raw_input) ^ ("full" in user_raw_input))):
                        await turn_context.send_activity("Invalid report style. Please choose from the provided options.")
                        await turn_context.send_activity(generate_format_selection_menu())
                        return # Stops execution entirely; never calls next_turn()
                elif(data_report_info["step"] == "ask delivery method"):
                    #Could actually validate with ai so that the input doesn't need to be gramatically perfect, but for now just check if the input is perfectly one of the two options
                    if(not(("email" in user_raw_input) ^ ("display" in user_raw_input))):
                        await turn_context.send_activity("Invalid delivery method. Please choose from the provided options.")
                        await turn_context.send_activity(generate_delivery_method_menu())
                        return # Stops execution entirely; never calls next_turn()
            # Elegant Mutation Example: Force uppercase or append guardrails
            # turn_context.activity.text = f"[Audited] {user_raw_input}"
            
            # Security/Validation Example: Short-circuiting execution
            # if "malicious_payload" in user_raw_input:
            #     await turn_context.send_activity("Input rejected due to policy.")
            #     return # Stops execution entirely; never calls next_turn()
            
        await conversation_state.save(turn_context)

        # Continue down the processing pipeline to the AgentApplication routes
        await next_turn()

adapter = CloudAdapter()
adapter.use(InputInterceptorMiddleware())

AGENT_APP = AgentApplication[TurnState](
    storage=storage, adapter=adapter
)

async def _other(turn_context: TurnContext, turn_state: TurnState):
    await turn_context.send_activity('You selected the "Other" option. Please specify your request or choose one of the available workflows.')

# async def validate_user_input(turn_context: TurnContext, turn_state: TurnState, expected_length_range=(2, 100)) -> bool:
#     """
#     Validates user input based on expected length range.
#     Returns True if valid, False otherwise.
#     """
#     user_text = turn_context.activity.text.strip() if turn_context.activity.text else ""
#     min_length, max_length = expected_length_range

#     if len(user_text) < min_length or len(user_text) > max_length:
#         await turn_context.send_activity(f"Input must be between {min_length} and {max_length} characters. Please try again.")
#         return False
#     return True

async def generate_data_report_summary(turn_context: TurnContext, data_report_info: dict, max_data_analysis_responses_stored: int) -> str:
    # TODO(1): encapsulate appending and trimming the ai_responses list into a function
    await turn_context.send_activity("⏳ Performing data analysis with AI model...")
    data_analysis_info = await data_analysis_accessor.get(turn_context, default_value_or_factory=lambda: copy.deepcopy(default_data_collection_info))
    try:
        data_report_info["ai_responses"].append(agent_core.generate_report(data_analysis_info, data_report_info["history"]["report_style"]))
    except Exception as e:
        Logger.error(f"Error generating report: {e}")
        await turn_context.send_activity(f"Error generating report. Please try again.")
        return "Error generating report."
    if(len(data_report_info["ai_responses"])>max_data_analysis_responses_stored):
        data_report_info["ai_responses"] = data_report_info["ai_responses"][-max_data_analysis_responses_stored:] # keep only the last responses
    pass  # Placeholder for future implementation of report summary generation logic

async def display_results_in_chunked_way(turn_context: TurnContext, display_beginning: str, ai_response: str):
    ai_response_sections = [s.strip() for s in ai_response.split("\n\n") if s.strip()]
    await turn_context.send_activity(display_beginning)
    for ai_response_section in ai_response_sections:
        await turn_context.send_activity(f"{ai_response_section}")

async def handle_conversation_logic(turn_context: TurnContext, turn_state: TurnState):
    """
    Core activity handler routing the conversation state and rendering 
    the selection menu or reacting to user choices.
    """
    user_text = turn_context.activity.text.strip() if turn_context.activity.text else ""

    await conversation_state.load(turn_context)

    user_action = await user_action_accessor.get(turn_context, default_value_or_factory=lambda: copy.deepcopy(default_user_action))

    #print(f"Current User Action: {user_action['user_action']}, User Input: {user_text}")

    # Check if the user selected one of our defined workflow paths
    if user_action['user_action'] == "Data Collection" or (user_action['user_action'] is None and "data collection" in user_text.lower()):
        user_action['user_action'] = "Data Collection"

        data_collection_info = await data_collection_accessor.get(turn_context, default_value_or_factory=lambda: copy.deepcopy(default_data_collection_info))

        # assume for now company name would be provided (would need to validate with AI model probably)
        #print(f"(1) Step Count: {data_collection_info['step_count']}, Current Step: {data_collection_info['step']}, User Input: {user_text}")

        Logger.info(f"Step Count: {data_collection_info['step_count']}, Current Step: {data_collection_info['step']}, User Input: {user_text}")

        if(data_collection_info["step_count"] > 0):
            if(data_collection_info["history"].get("company_name") is None):
                # save the company name to the data collection state history
                data_collection_info["history"]["company_name"] = user_text
                data_collection_info["step"] = "ask company topic"
            elif(data_collection_info["history"].get("company_topic") is None):
                # save the company topic to the data collection state history
                data_collection_info["history"]["company_topic"] = user_text
                data_collection_info["step"] = "ask timeframe"
            elif(data_collection_info["history"].get("timeframe") is None):
                # save the timeframe to the data collection state history
                data_collection_info["history"]["timeframe"] = user_text
                await turn_context.send_activity("⏳ Collecting data from AI model...")
                # TODO(1): encapsulate appending and trimming the ai_responses list into a function
                try:
                    data_collection_info["ai_responses"].append(agent_core.get_company_info(data_collection_info["history"]["company_name"], data_collection_info["history"]["company_topic"], data_collection_info["history"]["timeframe"]))
                except Exception as e:
                    Logger.error(f"Error generating report: {e}")
                    await turn_context.send_activity(f"Error generating report. Please try again.")
                    return "Error generating report."
                if(len(data_collection_info["ai_responses"])>max_data_collection_responses_stored):
                    data_collection_info["ai_responses"] = data_collection_info["ai_responses"][-max_data_collection_responses_stored:] # keep only the last 5 responses
                data_collection_info["step"] = "complete"

        data_collection_info["step_count"] += 1

        #print(f"(2) Step Count: {data_collection_info['step_count']}, Current Step: {data_collection_info['step']}, User Input: {user_text}")


        if data_collection_info["step"] == "ask company name":
            if("company_name" not in data_collection_info["history"]):
                await turn_context.send_activity("📊 Data Collection Module \n I'll help you collect company research data.\n Please enter the company name you want to research. (Must be 2-100 characters)")
        elif data_collection_info["step"] == "ask company topic":
            if("company_topic" not in data_collection_info["history"]):
                await turn_context.send_activity("Please enter the company topic you want to research. (Must be 2-100 characters)")
        elif data_collection_info["step"] == "ask timeframe":
            if("timeframe" not in data_collection_info["history"]):
                await turn_context.send_activity("Please enter the timeframe you want to research. (Must be 2-100 characters)")
        elif data_collection_info["step"] == "complete":
            await display_results_in_chunked_way(turn_context, f"✅ Data Collection Complete! Here's a brief summary of the company '{data_collection_info['history']['company_name']}' focusing on '{data_collection_info['history']['company_topic']}' within the timeframe of '{data_collection_info['history']['timeframe']}':",data_collection_info['ai_responses'][-1])
        # Trigger your data collection modules here

        # Update the local state cache with the modified dict properties
        await data_collection_accessor.set(turn_context, data_collection_info)
        
    elif user_action['user_action'] == "Data Analysis" or (user_action['user_action'] is None and "data analysis" in user_text.lower()):
        user_action['user_action'] = "Data Analysis"

        data_analysis_info = await data_analysis_accessor.get(turn_context, default_value_or_factory=lambda: copy.deepcopy(default_data_analysis_info))
        
        if(data_analysis_info["step_count"] > 0):
            if(data_analysis_info["history"].get("analysis_type") is None):
                # save the analysis type to the task state history
                data_analysis_info["history"]["analysis_type"] = user_text
                data_analysis_info["step"] = "complete"
                # TODO(1): encapsulate appending and trimming the ai_responses list into a function
                await turn_context.send_activity("⏳ Performing data analysis with AI model...")
                data_collection_info = await data_collection_accessor.get(turn_context, default_value_or_factory=lambda: copy.deepcopy(default_data_collection_info))
                try:
                    data_analysis_info["ai_responses"].append(agent_core.do_analysis_on_data_collections(data_collection_info, data_analysis_info["history"]["analysis_type"]))
                except Exception as e:
                    Logger.error(f"Error performing data analysis: {e}")
                    await turn_context.send_activity(f"Error performing data analysis. Please try again.")
                    return "Error performing data analysis."
                if(len(data_analysis_info["ai_responses"])>max_data_analysis_responses_stored):
                    data_analysis_info["ai_responses"] = data_analysis_info["ai_responses"][-max_data_analysis_responses_stored:] # keep only the last 5 responses
                #data_collection_info["ai_response"] = "Data analysis complete."
                #data_collection_info["ai_response"] = "Data analysis complete."

        data_analysis_info["step_count"] += 1

        if(data_analysis_info["step"] == "ask analysis type"):
            if("analysis_type" not in data_analysis_info["history"]):
                await turn_context.send_activity(generate_analysis_type_menu())
        elif(data_analysis_info["step"] == "complete"):
            await display_results_in_chunked_way(turn_context, f"✅ Data Analysis Complete! Here's a brief summary of the analysis type '{data_analysis_info['history']['analysis_type']}':",data_analysis_info['ai_responses'][-1])        # await turn_context.send_activity("Loading models to begin Data Analysis...")
        # Trigger your data analysis algorithms here
        
        await data_analysis_accessor.set(turn_context, data_analysis_info)
    elif user_action['user_action'] == "Report Generation" or (user_action['user_action'] is None and "report generation" in user_text.lower()):
        user_action['user_action'] = "Report Generation"

        data_report_info = await data_report_accessor.get(turn_context, default_value_or_factory=lambda: copy.deepcopy(default_data_report_info))

        if(data_report_info["step_count"] > 0):
            if(data_report_info["history"].get("report_style") is None):
                # save the report style to the task state history
                data_report_info["history"]["report_style"] = user_text
                data_report_info["step"] = "ask delivery method"
            elif(data_report_info["history"].get("delivery_method") is None): # TODO: actually send through email when delivery_method is 'email'
                # save the delivery method to the task state history
                data_report_info["history"]["delivery_method"] = user_text
                data_report_info["step"] = "ask email address" if "email" in data_report_info["history"]["delivery_method"].lower() else "complete"
                if(data_report_info["step"] == "complete"):
                    # generate the report summary
                    Logger.info(f"Generating report summary...")
                    await generate_data_report_summary(turn_context, data_report_info, max_data_analysis_responses_stored)
            elif(data_report_info["history"].get("email_address") is None and "email" in data_report_info["history"]["delivery_method"].lower()):
                # save the email address to the task state history
                data_report_info["history"]["email_address"] = user_text
                data_report_info["step"] = "complete"
                # generate the report summary
                await generate_data_report_summary(turn_context, data_report_info, max_data_analysis_responses_stored)

        data_report_info["step_count"] += 1

        if(data_report_info["step"] == "ask report style"):
            if("report_style" not in data_report_info["history"]):
                await turn_context.send_activity(generate_format_selection_menu())
        elif(data_report_info["step"] == "ask delivery method"):
            if("delivery_method" not in data_report_info["history"]):
                await turn_context.send_activity(generate_delivery_method_menu())
        elif(data_report_info["step"] == "ask email address"):
            if("email_address" not in data_report_info["history"]):
                await turn_context.send_activity("Please enter the email address where you would like the report to be sent.")
        elif(data_report_info["step"] == "complete"):
            if("display" in data_report_info["history"].get("delivery_method").lower()):
                #display the report summary directly in the chat
                await display_results_in_chunked_way(turn_context, f"✅ Report Generation Complete! Here's a brief summary of the report style '{data_report_info['history']['report_style']}' with delivery method '{data_report_info['history']['delivery_method']}':",data_report_info['ai_responses'][-1])
            else:
                # send the report summary to the provided email address (this is a placeholder; actual email sending logic would be implemented here)
                # 
                await turn_context.send_activity(f"✅ Report Generation Complete! The report would technically be sent (but for demonstration purposes it won't be sent to keep project concise as a proof of concept focused on AI and not email delivery) to '{data_report_info['history']['email_address']}' with the report style '{data_report_info['history']['report_style']}'.\n")
        # Trigger your reporting logic here

        await data_report_accessor.set(turn_context, data_report_info)
        
    else:
        # Default fallback: Render the selection menu with Suggested Actions
        reply_activity = generate_selection_menu()
        
        await turn_context.send_activity(reply_activity)

    await user_action_accessor.set(turn_context, user_action)
    # Save the updated memory state cache directly back into persistent storage
    await conversation_state.save(turn_context)

    #print("technically saved state")

#AGENT_APP.conversation_update("membersAdded")(handle_conversation_logic)

async def handle_conversation_reset(turn_context: TurnContext, turn_state: TurnState):
    """
    Resets the conversation state and presents the initial selection menu to the user.
    """
    Logger.info("[PLAYGROUND RESET]: Wiping conversation state...")
    await conversation_state.load(turn_context)

    # Clear all conversation state properties

    await asyncio.gather(
        user_action_accessor.set(turn_context, copy.deepcopy(default_user_action)),
        data_collection_accessor.set(turn_context, copy.deepcopy(default_data_collection_info)),
        data_analysis_accessor.set(turn_context, copy.deepcopy(default_data_analysis_info)),
        data_report_accessor.set(turn_context, copy.deepcopy(default_data_report_info))
    )

    # Save the cleared state back to persistent storage
    await conversation_state.save(turn_context)

    # Notify the user that the conversation state has been reset
    await turn_context.send_activity("🔄 Conversation state has been entirely wiped clean! You can start over.")
    await turn_context.send_activity(f"/menu to return to main menu, /clear command is available to reset the conversation state at any time.")
    # Present the initial selection menu to the user
    await handle_conversation_logic(turn_context, turn_state)

@AGENT_APP.conversation_update("membersAdded")
async def members_added(turn_context: TurnContext, turn_state: TurnState):
    """
    Handles the conversation update event when new members are added to the conversation.
    This is typically used to reset the conversation state and present the initial selection menu.
    """
    # Reset the conversation state for a fresh start
    #if(conversation_state):
    #    await conversation_state.clear(turn_context)
    for member in turn_context.activity.members_added:
        if member.id != turn_context.activity.recipient.id:
            await handle_conversation_reset(turn_context, turn_state)

async def reset_data_collection_prompt_flow(turn_context: TurnContext):
    data_collection_info = await data_collection_accessor.get(turn_context, default_value_or_factory=lambda: copy.deepcopy(default_data_collection_info))
    data_collection_info["step"] = copy.deepcopy(default_data_collection_info["step"])
    data_collection_info["history"] = copy.deepcopy(default_data_collection_info["history"])
    data_collection_info["step_count"] = copy.deepcopy(default_data_collection_info["step_count"])
    #print("new step: ",data_collection_info["step"])
    #print("new step count: ",data_collection_info["step_count"])
    await data_collection_accessor.set(turn_context, data_collection_info)

async def reset_data_analysis_prompt_flow(turn_context: TurnContext):
    data_analysis_info = await data_analysis_accessor.get(turn_context, default_value_or_factory=lambda: copy.deepcopy(default_data_analysis_info))
    data_analysis_info["step"] = copy.deepcopy(default_data_analysis_info["step"])
    data_analysis_info["history"] = copy.deepcopy(default_data_analysis_info["history"])
    data_analysis_info["step_count"] = copy.deepcopy(default_data_analysis_info["step_count"])
    await data_analysis_accessor.set(turn_context, data_analysis_info)

async def reset_data_report_prompt_flow(turn_context: TurnContext):
    data_report_info = await data_report_accessor.get(turn_context, default_value_or_factory=lambda: copy.deepcopy(default_data_report_info))
    data_report_info["step"] = copy.deepcopy(default_data_report_info["step"])
    data_report_info["history"] = copy.deepcopy(default_data_report_info["history"])
    data_report_info["step_count"] = copy.deepcopy(default_data_report_info["step_count"])
    await data_report_accessor.set(turn_context, data_report_info)
async def handle_return_to_main_menu(turn_context: TurnContext, turn_state: TurnState):
    """
    Handles the command to return to the main menu.
    Resets the conversation state and presents the initial selection menu.
    """
    Logger.info("[RETURN TO MAIN MENU]: Resetting conversation state...")
    await conversation_state.load(turn_context)

    await asyncio.gather(
        user_action_accessor.set(turn_context, copy.deepcopy(default_user_action)),
        reset_data_collection_prompt_flow(turn_context),
        reset_data_analysis_prompt_flow(turn_context),
        reset_data_report_prompt_flow(turn_context)
    )

    await conversation_state.save(turn_context)

    await handle_conversation_logic(turn_context, turn_state)

AGENT_APP.message("/menu")(handle_return_to_main_menu)
AGENT_APP.message("/clear")(handle_conversation_reset)
AGENT_APP.message("/other")(_other)

# @AGENT_APP.activity("message")
# async def on_message(turn_context: TurnContext, turn_state: TurnState):
#     await turn_context.send_activity(f"you said: {turn_context.activity.text}")

AGENT_APP.activity("message")(handle_conversation_logic)


if __name__ == "__main__":
    try:
        start_server(AGENT_APP, None)
    except Exception as error:
        raise error