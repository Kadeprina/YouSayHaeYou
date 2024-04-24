import json
import requests
from langchain.tools import BaseTool
from langchain.agents import AgentType, initialize_agent, Tool
from langchain.chat_models import ChatOpenAI

from typing import Optional, Type
from pydantic import BaseModel, Field


class ProductInput(BaseModel):
    """Get the product information."""
    query_string: str = Field(...,
                              description="The keyword for searching the product.")
    max_price: float = Field(...,
                             description="The maximum price of the product.")
    min_price: float = Field(...,
                             description="The minimum price of the product.")
    special_price: bool = Field(...,
                                description="Whether the product is on sale.")
    point: bool = Field(...,
                        description="Whether the product has LINE Point reward.")
    line_badge: bool = Field(...,
                             description="Whether the product is sold by 官方直營.")
    line_pay: bool = Field(...,
                           description="Whether the product can be paid by LINE Pay.")
    color: list = Field(...,
                        description="The color string of the product. e.g. [VIOLET,WHITE,BLACK]")


class ProductTool(BaseTool):
    name = "search_product"
    description = "Get the product information"

    def _run(self, query_string: str, max_price: float, min_price: float, special_price: bool, point: bool,
             line_badge: bool, line_pay: bool, color: list):
        product_results = get_product(query_string,
                                      max_price,
                                      min_price,
                                      special_price,
                                      point,
                                      line_badge,
                                      line_pay,
                                      color)
        return product_results

    def _arun(self, query_string: str, max_price: float, min_price: float, special_price: bool, point: bool,
              line_badge: bool, line_pay: bool, color: list):
        raise NotImplementedError("This tool does not support async")

    args_schema: Optional[Type[BaseModel]] = ProductInput


# From LINE SHOPPING Product Search API.
def get_product(query_string, max_price, min_price, special_price, point, line_badge, line_pay, color):
    # def get_product(query_string):
    url = "https://ec-gpt-plugin.vercel.app/api/get-product"

    # Build the payload
    payload = {
        "queryString": query_string
    }

    # Only add the optional parameters to the payload if they are provided
    if max_price > 10:
        payload["maxPrice"] = max_price
    if min_price > 10:
        payload["minPrice"] = min_price
    if special_price is not None:
        payload["specialPrice"] = special_price
    if point is not None:
        payload["point"] = point
    if line_badge is not None:
        payload["lineBadge"] = line_badge
    if line_pay is not None:
        payload["linePay"] = line_pay
    if color:
        payload["color"] = color

    headers = {
        "Content-Type": "application/json"
    }

    # Send POST request
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        # Parse and return the JSON response body
        # Get the JSON response
        data = response.json()
        # Limit the number of products to 10
        if 'products' in data:
            # Remove 'allMerchants' and 'merchant' from each product
            for product in data['products']:
                if 'allMerchants' in product:
                    del product['allMerchants']
                if 'merchant' in product:
                    del product['merchant']
            data['products'] = data['products'][:10]
        return data
    else:
        # If the request failed, raise an exception
        response.raise_for_status()


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
    tools = [TravelPOITool(), TravelExpTool(), ProductTool()]
    open_ai_agent = initialize_agent(tools,
                                     model,
                                     agent=AgentType.OPENAI_FUNCTIONS,
                                     verbose=True)
    tool_result = open_ai_agent.run(input)

    return tool_result
