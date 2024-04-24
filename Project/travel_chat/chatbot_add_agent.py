import json
import requests
from langchain.tools import BaseTool
from langchain.agents import AgentType, initialize_agent, Tool
from langchain.chat_models import ChatOpenAI

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
