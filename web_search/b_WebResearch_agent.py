prompt_template = """
    Answer the following questions as best you can. You have access to the following tools:

    {tools}

    Use the following format:

    Question: the input question you must answer
    Thought: you should always think about what to do
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question

    Begin!

    {agent_scratchpad}

    Question: {input}
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import Tool

load_dotenv()

def get_current_time(*args, **kwargs):
    import datetime
    return datetime.datetime.now().strftime("%H:%M:%S")


def format_results(document):
    return {
        "content": document.page_content,
        "title": document.metadata["title"],
        "url": document.metadata["source"]
    }
def search_the_web(query:str) -> str:
    from a_WebResearchRetriever import simple_search 
    results = simple_search(query)
    results = [format_results(result) for result in results]
    return results

tools=[
    Tool(name="get_current_time", func=get_current_time,
          description="Get the current time in the format 'HH:MM:SS'"),
    Tool(name="search_the_web", func=search_the_web,
           description="Search the web for any information needed and get back a list of objects of {content, title, url} for each result")
]

#model = ChatOpenAI( model="gpt-4o" )

model = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL")
)

prompt = ChatPromptTemplate.from_template(prompt_template)

agent = create_react_agent(
    llm= model, tools=tools, 
    prompt = prompt , 
    stop_sequence=True)

agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)


if __name__ == "__main__":  

    # Run the agent with a test query
    #response = agent_executor.invoke({"input": "What are the latest news? Respond in Greek."})
    #print("response:", response)

    while True:
        q = input("Ask a question: ")
        if q == "exit":
            break
        # if q == "print":   
        #     print_messages(messages)
        #     continue

        response = agent_executor.invoke({"input": q})

        print(response)

