import json
import requests
from langchain.tools import BaseTool
from langchain.agents import AgentType, initialize_agent, AgentExecutor, create_react_agent, Tool
from langchain.chat_models import ChatOpenAI
from ionic_langchain.tool import Ionic, IonicTool
from langchain import hub

from typing import Optional, Type
from pydantic import BaseModel, Field


class TravelPOIInput(BaseModel):
    """Get the keyword about travel information."""

    keyword: str = Field(...,
                         description="The city and state, e.g. San Francisco, CA")


class TravelPOITool(BaseTool):
    name = "search_poi"
    description = "Get the keyword about travel information"

    def _run(self, keyword: str):
        poi_results = get_pois(keyword)

        return poi_results

    def _arun(self, keyword: str):
        raise NotImplementedError("This tool does not support async")

    args_schema: Optional[Type[BaseModel]] = TravelPOIInput


def get_pois(keyword):
    """
    Query the get-poi API with the provided keyword.

    Parameters:
    keyword (str): The keyword for searching the position of interest.

    Returns:
    dict: The response from the API, should comply with getPoiResponse schema.
    """
    url = "https://nextjs-chatgpt-plugin-starter.vercel.app/api/get-poi"
    headers = {'Content-Type': 'application/json'}

    # The request data should comply with searchPoiRequest schema
    data = {"keyword": keyword}

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.text}


class TravelExpInput(BaseModel):
    """Get the keyword about travel experience."""

    keyword: str = Field(...,
                         description="The city and state, e.g. San Francisco, CA")


class TravelExpTool(BaseTool):
    name = "search_experience"
    description = "Get the keyword about travel experience"

    def _run(self, keyword: str):
        exp_results = get_experience(keyword)
        return exp_results

    def _arun(self, keyword: str):
        raise NotImplementedError("This tool does not support async")

    args_schema: Optional[Type[BaseModel]] = TravelExpInput


def get_experience(keyword):
    api_url = "https://nextjs-chatgpt-plugin-starter.vercel.app/api/get-experience"
    headers = {'Content-Type': 'application/json'}

    data = {
        "keyword": keyword
    }

    response = requests.post(api_url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        return response.json()
    else:
        return None


def all_in_1_agent(input):
    model = ChatOpenAI(model="gpt-4-turbo")
    tools = [TravelPOITool(), TravelExpTool()]
    open_ai_agent = initialize_agent(tools,
                                     model,
                                     agent=AgentType.OPENAI_FUNCTIONS,
                                     verbose=True)
    tool_result = open_ai_agent.run(input)

    return tool_result


def search_products():
    llm = ChatOpenAI(model="gpt-4-turbo")

    ionic_tool = IonicTool().tool()

    # The tool comes with its own prompt,
    # but you may also update it directly via the description attribute:

    ionic_tool.description = str(
        """
    Ionic is an e-commerce shopping tool. Assistant uses the Ionic Commerce Shopping Tool to find, discover, and compare products from thousands of online retailers. Assistant should use the tool when the user is looking for a product recommendation or trying to find a specific product.

    The user may specify the number of results, minimum price, and maximum price for which they want to see results.
    Ionic Tool input is a comma-separated string of values:
      - query string (required, must not include commas)
      - number of results (default to 4, no more than 10)
      - minimum price in cents ($5 becomes 500)
      - maximum price in cents
    For example, if looking for coffee beans between 5 and 10 dollars, the tool input would be `coffee beans, 5, 500, 1000`.

    Return them as a markdown formatted list with each recommendation from tool results, being sure to include the full PDP URL. For example:

    1. Product 1: [Price] -- link
    2. Product 2: [Price] -- link
    3. Product 3: [Price] -- link
    4. Product 4: [Price] -- link
    """
    )

    tools = [ionic_tool]

    # default prompt for create_react_agent
    prompt = hub.pull("hwchase17/react")

    agent = create_react_agent(
        llm,
        tools,
        prompt=prompt,
    )

    agent_executor = AgentExecutor(
        agent=agent, tools=tools, handle_parsing_errors=True, verbose=True, max_iterations=5
    )

    return agent_executor
