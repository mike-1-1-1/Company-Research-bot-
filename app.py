# app.py
from microsoft_agents.hosting.core import (
   AgentApplication,
   TurnState,
   TurnContext,
   MemoryStorage,
   ConversationState
)
from microsoft_agents.hosting.aiohttp import CloudAdapter
from start_server import start_server

from microsoft_agents.activity import Activity, ActivityTypes, SuggestedActions, CardAction

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

storage = MemoryStorage()

conversation_state = ConversationState(storage)

user_action_accessor = conversation_state.create_property("user_action")

data_collection_accessor = conversation_state.create_property("data_collection_accessor")
data_analysis_accessor = conversation_state.create_property("data_analysis_accessor")
data_report_accessor = conversation_state.create_property("data_report_accessor")


AGENT_APP = AgentApplication[TurnState](
    storage=storage, adapter=CloudAdapter()
)

async def _other(turn_context: TurnContext, turn_state: TurnState):
    await turn_context.send_activity('You selected the "Other" option. Please specify your request or choose one of the available workflows.')

async def handle_conversation_logic(turn_context: TurnContext, turn_state: TurnState):
    """
    Core activity handler routing the conversation state and rendering 
    the selection menu or reacting to user choices.
    """
    user_text = turn_context.activity.text.strip() if turn_context.activity.text else ""

    await conversation_state.load(turn_context)

    user_action = await user_action_accessor.get(turn_context, default_value_or_factory=lambda: {"user_action":None})

    print(f"Current User Action: {user_action['user_action']}, User Input: {user_text}")

    # Check if the user selected one of our defined workflow paths
    if user_action['user_action'] == "Data Collection" or (user_action['user_action'] is None and "data collection" in user_text.lower()):
        user_action['user_action'] = "Data Collection"

        data_collection_info = await data_collection_accessor.get(turn_context, default_value_or_factory=lambda: {"step": "ask company name", "history": {}, "step_count" : 0})

        # assume for now company name would be provided (would need to validate with AI model probably)
        print(f"(1) Step Count: {data_collection_info['step_count']}, Current Step: {data_collection_info['step']}, User Input: {user_text}")

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
                data_collection_info["step"] = "complete"
                

        data_collection_info["step_count"] += 1

        print(f"(2) Step Count: {data_collection_info['step_count']}, Current Step: {data_collection_info['step']}, User Input: {user_text}")


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
            await turn_context.send_activity(f"would technically research {data_collection_info['history']['company_name']} on the topic of {data_collection_info['history']['company_topic']} for the timeframe of {data_collection_info['history']['timeframe']}.")
        # Trigger your data collection modules here

        # Update the local state cache with the modified dict properties
        await data_collection_accessor.set(turn_context, data_collection_info)
        
    elif user_action['user_action'] == "Data Analysis" or (user_action['user_action'] is None and "data analysis" in user_text.lower()):
        user_action['user_action'] = "Data Analysis"

        data_analysis_info = await data_analysis_accessor.get(turn_context, default_value_or_factory=lambda: {"step": "ask analysis type", "history": {}, "step_count" : 0})
        
        if(data_analysis_info["step_count"] > 0):
            if(data_analysis_info["history"].get("analysis_type") is None):
                # save the analysis type to the task state history
                data_analysis_info["history"]["analysis_type"] = user_text
                data_analysis_info["step"] = "complete"

        data_analysis_info["step_count"] += 1

        if(data_analysis_info["step"] == "ask analysis type"):
            if("analysis_type" not in data_analysis_info["history"]):
                await turn_context.send_activity(generate_analysis_type_menu())
        else:
            await turn_context.send_activity(f"would technically perform {data_analysis_info['history']['analysis_type']}.")
        # await turn_context.send_activity("Loading models to begin Data Analysis...")
        # Trigger your data analysis algorithms here
        
        await data_analysis_accessor.set(turn_context, data_analysis_info)
    elif user_action['user_action'] == "Report Generation" or (user_action['user_action'] is None and "report generation" in user_text.lower()):
        user_action['user_action'] = "Report Generation"

        data_report_info = await data_report_accessor.get(turn_context, default_value_or_factory=lambda: {"step": "ask report style", "history": {}, "step_count" : 0})

        if(data_report_info["step_count"] > 0):
            if(data_report_info["history"].get("report_style") is None):
                # save the report style to the task state history
                data_report_info["history"]["report_style"] = user_text
                data_report_info["step"] = "complete"


        data_report_info["step_count"] += 1

        if(data_report_info["step"] == "ask report style"):
            if("report_style" not in data_report_info["history"]):
                await turn_context.send_activity(generate_format_selection_menu())
        else:
            await turn_context.send_activity("Would technically generate a report in the style of " + data_report_info['history']['report_style'] + ".")
        # Trigger your reporting logic here

        await data_report_accessor.set(turn_context, data_report_info)
        
    else:
        # Default fallback: Render the selection menu with Suggested Actions
        reply_activity = generate_selection_menu()
        
        await turn_context.send_activity(reply_activity)

    await user_action_accessor.set(turn_context, user_action)
    # Save the updated memory state cache directly back into persistent storage
    await conversation_state.save(turn_context)

    print("technically saved state")

AGENT_APP.conversation_update("membersAdded")(handle_conversation_logic)

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