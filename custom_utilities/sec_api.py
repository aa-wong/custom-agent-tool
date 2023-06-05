#!/usr/bin/env python
# coding: utf-8

# In[7]:


"""Util that calls SEC API."""
from typing import Any, Dict, Optional
import aiohttp
import requests
from pydantic.class_validators import root_validator
from pydantic.main import BaseModel
from langchain.utils import get_from_dict_or_env


# In[ ]:


from langchain.document_loaders.base import Document
from langchain.indexes import VectorstoreIndexCreator
from langchain.utilities import ApifyWrapper


# In[29]:


class SecAPIWrapper(BaseModel):
    """
    Wrapper around the SEC API.
    """

    c: str = "us"
    hl: str = "en"
    ps: int = 10
    type: str = "search"  # search, latest_headlines, sources
    sec_api_key: Optional[str] = None
    aiosession: Optional[aiohttp.ClientSession] = None

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that api key exists in environment."""
        sec_api_key = get_from_dict_or_env(
            values, "sec_api_key", "SEC_API_KEY"
        )
        values["sec_api_key"] = sec_api_key

        return values

    def results(self, query: str, ticker: str, start_date: str, end_date: str, **kwargs: Any) -> Dict:
        """Run query through SEC."""
        return self._sec_search_results(
            query,
            ticker,
            start_date,
            end_date,
            **kwargs,
        )

    def run(self, query: str, ticker: str, start_date: str, end_date: str, **kwargs: Any) -> str:
        """Run query through SEC and parse result."""
        results = self._sec_search_results(
            query,
            ticker,
            start_date,
            end_date,
            **kwargs,
        )

        return self._parse_results(results)

    async def aresults(self, query: str, **kwargs: Any) -> Dict:
        """Run query through GoogleSearch."""
        results = await self._async_sec_search_results(
            query,
            countries=self.c,
            lang=self.hl,
            page_size=self.ps,
            search_type=self.type,
            **kwargs,
        )
        return results

    async def arun(self, query: str, **kwargs: Any) -> str:
        """Run query through GoogleSearch and parse result async."""
        results = await self._async_sec_search_results(
            query,
            countries=self.c,
            lang=self.hl,
            page_size=self.ps,
            search_type=self.type,
            **kwargs,
        )

        return self._parse_results(results)

    def _parse_results(self, results: dict) -> str:
        filings = results.get("filings")

        if len(filings) < 1:
            return "No results was found"
        
        filings = filings[0:9]
        snippets = []
        
        for filing in filings:
            company_name = filing.get("companyNameLong")
            ticker = filing.get("ticker")
            description = filing.get("description")
            form_type = filing.get("formType")
            url = filing.get("filingUrl")
            filed_at = filing.get("filedAt")

            snippet = (
                f"Company Name: {company_name}\n"
                f"Ticker: {ticker}\n"
                f"Description: {description}\n"
                f"Form Type: {form_type}\n"
                f"URL: {url}\n"
                f"Filed At: {filed_at}"
            )
                
            snippets.append(snippet)

        return " ".join(snippets)

    def _sec_search_results(
        self, search_term: str, ticker: str, start_date: str, end_date: str, **kwargs: Any
    ) -> dict:

        headers = {
            "Authorization": self.sec_api_key or "",
            "Content-Type": "application/json",
        }
        params = {
            "query": search_term,
            "ticker": ticker,
            "formTypes": [
                "8-K",
                "10-Q",
                "10-K"
            ],
            "startDate": start_date,
            "endDate": end_date,
            **{key: value for key, value in kwargs.items() if value is not None},
        }
        
        response = requests.post(f"https://api.sec-api.io/full-text-search", json=params, headers=headers)
        response.raise_for_status()
        return response.json()

    async def _async_sec_search_results(
        self, search_term: str, search_type: str = "search", **kwargs: Any
    ) -> dict:
        headers = {
            "Authorization": self.sec_api_key or "",
            "Content-Type": "application/json",
        }
        url = f"https://api.newscatcherapi.com/v2/{search_type}"
        params = {
            "query": search_term,
            "ticker": ticker,
            "formTypes": [
                "8-K",
                "10-Q",
                "10-K"
            ],
            "startDate": start_date,
            "endDate": end_date,
            **{key: value for key, value in kwargs.items() if value is not None},
        }

        if not self.aiosession:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, params=params, headers=headers, raise_for_status=False
                ) as response:
                    search_results = await response.json()
        else:
            async with self.aiosession.post(
                url, params=params, headers=headers, raise_for_status=True
            ) as response:
                search_results = await response.json()

        return search_results

