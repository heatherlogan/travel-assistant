import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tools import create_todo_list_tool, add_todo_item_tool, final_answer_tool
from document_tools import document_tools
from langchain_core.runnables.base import RunnableSerializable
from langchain_core.messages import ToolMessage
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from dotenv import load_dotenv
from middleware import create_middleware_stack

load_dotenv()


def get_agent_prompt():
    return ChatPromptTemplate.from_messages([
        ("system", (
            "You're a helpful travel planner assistant. "
        
            "You can provide general advice but also create and maintain todo lists using tools."

            "You have access to a document store containing the users travel plans, todo lists, and budgets. "
            "Use the following context from these documents to answer users queries or before using any tools:\n"

            "{context}\n\n"
            
            "Conversation Context:\n{conversation_context}\n\n"
            
            "Available Documents Summary:\n{document_summary}\n\n"
            
            "First assess whether the user query requires use of the tools, or if you can answer directly."
            "After using a tool the tool output will be provided in the "
            " 'scratchpad' below. If you have an answer in the "
            "scratchpad you should not use any more tools and "
            "instead answer directly to the user."
            )),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

tools = [
    create_todo_list_tool,
    add_todo_item_tool,
    final_answer_tool,
] + document_tools

llm = ChatOpenAI(
    model_name="gpt-4o",
    max_retries=3,
    openai_api_key=os.getenv('OPENAI_API_KEY')
    )

class CustomAgentExecutor:
    chat_history: list[BaseMessage]

    def name2tool(self, name: str):
        tool_map = {tool.name: tool.func for tool in tools}
        return tool_map.get(name)
    

    def __init__(self, max_iterations: int = 3):
        self.chat_history = []
        self.max_iterations = max_iterations
        self.middleware = create_middleware_stack()
        
        # Create prompt without context parameter
        self.prompt_template = get_agent_prompt()
        
        agent_llm = ChatOpenAI(
            model_name="gpt-4o",
            max_retries=3,
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        self.agent_llm = agent_llm

    def invoke(self, input: str, conversation_history: list = None) -> dict:
        # Use middleware to enhance the query with context
        enhanced_query = self.middleware['query_enhancement'].enhance_query(input)
        context = enhanced_query.get('context', '')
        document_summary = json.dumps(enhanced_query.get('document_summary', {}), indent=2)
        
        # Get conversation context
        conversation_context = ""
        if conversation_history:
            conversation_context = self.middleware['conversation'].process_conversation_context(
                input, conversation_history
            )
        
        # Create the agent with enhanced context
        agent = (
            {
                "input": lambda x: x["input"],
                "context": lambda x: x["context"],
                "conversation_context": lambda x: x["conversation_context"],
                "document_summary": lambda x: x["document_summary"],
                "chat_history": lambda x: x["chat_history"],
                "agent_scratchpad": lambda x: x.get("agent_scratchpad", [])
            }
            | self.prompt_template
            | self.agent_llm.bind_tools(tools, tool_choice="any")
        )
        
        # invoke the agent but we do this iteratively in a loop until
        # reaching a final answer
        count = 0
        agent_scratchpad = []
        while count < self.max_iterations:
            # invoke a step for the agent to generate a tool call
            tool_call = agent.invoke({
                "input": input,
                "context": context,
                "conversation_context": conversation_context,
                "document_summary": document_summary,
                "chat_history": self.chat_history,
                "agent_scratchpad": agent_scratchpad
            })
            # add initial tool call to scratchpad
            agent_scratchpad.append(tool_call)
            # otherwise we execute the tool and add it's output to the agent scratchpad
            tool_name = tool_call.tool_calls[0]["name"]
            tool_args = tool_call.tool_calls[0]["args"]
            tool_call_id = tool_call.tool_calls[0]["id"]
            tool_out = self.name2tool(tool_name)(**tool_args)
            # add the tool output to the agent scratchpad
            tool_exec = ToolMessage(
                content=f"{tool_out}",
                tool_call_id=tool_call_id
            )
            agent_scratchpad.append(tool_exec)
            # add a print so we can see intermediate steps
            print(f"{count}: {tool_name}({tool_args})")
            count += 1
            # if the tool call is the final answer tool, we stop
            if tool_name == "final_answer_tool":
                break
        # add the final output to the chat history
        if isinstance(tool_out, dict) and "answer" in tool_out:
            final_answer = tool_out["answer"]
        else:
            # For non-final-answer tools, use the tool output as the final answer
            final_answer = str(tool_out)
        
        self.chat_history.extend([
            HumanMessage(content=input),
            AIMessage(content=final_answer)
        ])
        # return the final answer in dict form
        if isinstance(tool_out, dict):
            return json.dumps(tool_out)
        else:
            return json.dumps({"answer": final_answer, "tools_used": []})