from langchain_core.tools import tool
from aire.services.memory import post_event

# Define the tools for the agent to use
@tool
def add_event_to_database(date, subject):
    """Call to add event to database.
    
    Args:
        date: event date
        subject: event subject
    """
    if(date and subject):
        # post_event({date, subject})
        return {date, subject}
    else:
        return False
    
Tools = [add_event_to_database]