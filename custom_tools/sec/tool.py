"""Tool for the Serper.dev Google Search API."""

from typing import Optional, Type
from pydantic.fields import Field
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.tools.base import BaseTool, BaseModel
from custom_agent_tools.custom_utilities.sec_api import SecAPIWrapper

class SearchSchema(BaseModel):
    query: str = Field(description="should be a search query")
    ticker: str = Field(description="should be a stock ticker symbol")
    start_date: str = Field(description="should be a start date in the format of YYYY-MM-DD")
    end_date: str = Field(description="should be a end date in the format of YYYY-MM-DD")


class SecTool(BaseTool):
    """Tool that adds the capability to query SEC API."""

    name = "SEC"
    description = (
        "A search engine for looking up 8-K, 10-Q, or 10-K filings for a specific company."
        "Only use after using normal search and when knowing which specific filling is being requested"
        "Input should be a search query, ticker symbol, start date and end date."
    )
    args_schema: Type[SearchSchema] = SearchSchema
    api_wrapper: SecAPIWrapper  = Field(default_factory=SecAPIWrapper)

    def _run(
        self,
        query: str,
        ticker: str,
        start_date: str,
        end_date: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        return str(self.api_wrapper.run(query, ticker, start_date, end_date))

    async def _arun(
        self,
        query: str,
        ticker: str,
        start_date: str,
        end_date: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        return (await self.api_wrapper.arun(query, ticker, start_date, end_date)).__str__()