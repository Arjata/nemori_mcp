from dotenv import load_dotenv
load_dotenv()

import asyncio
from typing import List, Dict, Any
from enum import Enum
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP
from nemori import NemoriMemory, MemoryConfig

LOCKED_USER_ID = "__user__"

config = MemoryConfig(enable_semantic_memory=True, enable_prediction_correction=True)
memory = NemoriMemory(config=config)

mcp = FastMCP("NemoriMemoryService")
print(f"MCP Nemori Memory Service starting...")

class Message(BaseModel):
    role: str
    content: str

class SearchMethod(str, Enum):
    HYBRID = "hybrid"
    BM25 = "bm25"
    VECTOR_NORLIFT = "vector_norlift"
    VECTOR = "vector"

@mcp.tool()
async def add_user_messages(messages: List[Message]) -> Dict[str, Any]:
    """
    RECORD a conversation turn into persistent memory. This is the primary method for saving information.

    **Usage Rules:**

    1.  **FIRST TURN (MANDATORY):** If this is the first turn of the conversation, you MUST call this tool to
        establish the initial memory context.

    2.  **HANDLING NEW INFORMATION (MANDATORY):** When the user introduces a topic, item, opinion, or preference
        that appears new in the current conversation, you MUST acknowledge this new information in your response.
        This confirms you've understood and will remember it. You should then immediately call this tool to save the turn.
        **You do not need to search before acknowledging new information.**

    3.  **MANDATORY CALL (ALL TURNS):** You MUST call this tool after every single interaction turn is complete.
        The `messages` list must always include the last user message and your final response for that turn.

    Example Workflow for New Information:
    1. User: "My favorite color is blue."
    2. Your Assistant Response: "Blue is a great choice. I'll keep that in mind."
    3. Your Tool Call: `add_user_messages(messages=[{"role": "user", "content": "My favorite color is blue."}, {"role": "assistant", "content": "Blue is a great choice. I'll keep that in mind."}])`
    """
    print(f"Adding {len(messages)} messages for locked user '{LOCKED_USER_ID}'...")
    message_dicts = [msg.model_dump() for msg in messages]
    
    memory.add_messages(user_id=LOCKED_USER_ID, messages=message_dicts)
    memory.flush(LOCKED_USER_ID)
    await asyncio.to_thread(memory.wait_for_semantic, LOCKED_USER_ID)
    
    print(f"Semantic processing complete for locked user '{LOCKED_USER_ID}'.")
    return {
        "status": "success",
        "message": f"{len(messages)} messages added and processed."
    }

@mcp.tool()
def search_user_memory(
    query: str,
    search_method: SearchMethod = SearchMethod.HYBRID
) -> List[Dict[str, Any]]:
    """
    RETRIEVE information from memory to inform your responses or recall past conversations.

    **Usage Rules:**

    1.  **CONTEXTUAL KICKSTART (MANDATORY):** At the beginning of a new conversation, you MUST perform a search
        to gather context about past interactions before responding. On the very first turn, this search will
        return empty, which correctly confirms that you need to establish a new context.
        Example Query: "summary of recent topics and key user interests"

    2.  **SEARCH TO ANSWER (MANDATORY):** When the user asks a question that requires information from the past,
        you MUST use this tool to find the answer in your memory.
        Example: User asks "Do you remember my favorite color?" -> `search_user_memory(query="user's favorite color")`
        Example: User asks "What was that project name we talked about?" -> `search_user_memory(query="project name")`

    **Query Formulation:**
    - Formulate a clear and concise question describing the information you need.

    **Response Generation:**
    - After using this tool, you must synthesize the search results into a smooth and natural conversational response.
    - Your final response to the user MUST NOT contain any source identifiers, citation marks, or metadata.
    """
    print(f"Searching for '{query}' in memory for locked user '{LOCKED_USER_ID}' using '{search_method.value}' method...")
    
    search_results_dict = memory.search(
        LOCKED_USER_ID,
        query,
        search_method=search_method.value
    )
    
    episodic_results = search_results_dict.get('episodic', [])
    semantic_results = search_results_dict.get('semantic', [])
    
    combined_results = episodic_results + semantic_results
    
    print(f"Found {len(combined_results)} combined results from episodic and semantic search.")
    
    return combined_results

if __name__ == "__main__":
    try:
        mcp.run()
    finally:
        print(f"Shutting down MCP service...")
        memory.close()
        print("Nemori memory closed.")
