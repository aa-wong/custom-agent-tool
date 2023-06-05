"""Tool for the Serper.dev Google Search API."""

from typing import Optional
from pydantic.fields import Field
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.tools.base import BaseTool
from custom_agent_tools.custom_utilities.newscatcher_api import NewscatcherAPIWrapper

class NewscatcherTool(BaseTool):
    """Tool that adds the capability to query the Serper.dev Google search API."""

    name = "Newscatcher"
    description = (
        "Useful for when looking up relevant news articles."
        "Use this more than the SEC action earnings and spending"
        "Input should be a search query."
    )
    api_wrapper: NewscatcherAPIWrapper  = Field(default_factory=NewscatcherAPIWrapper)

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        return str(self.api_wrapper.run(query))

    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        return (await self.api_wrapper.arun(query)).__str__()