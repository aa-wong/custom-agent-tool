#!/usr/bin/env python
# coding: utf-8

# In[1]:


"""Util that calls Newscatcher API."""
from typing import Any, Dict, Optional


# In[2]:


import aiohttp
import requests
from pydantic.class_validators import root_validator
from pydantic.main import BaseModel


# In[3]:


from langchain.utils import get_from_dict_or_env


# In[4]:


class NewscatcherAPIWrapper(BaseModel):
    """
    Wrapper around the Newscatcher API.
    """

    c: str = "us"
    hl: str = "en"
    ps: int = 10
    type: str = "search"  # search, latest_headlines, sources
    newscatcher_api_key: Optional[str] = None
    aiosession: Optional[aiohttp.ClientSession] = None

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that api key exists in environment."""
        newscatcher_api_key = get_from_dict_or_env(
            values, "newscatcher_api_key", "NEWSCATCHER_API_KEY"
        )
        values["newscatcher_api_key"] = newscatcher_api_key

        return values

    def results(self, query: str, **kwargs: Any) -> Dict:
        """Run query through GoogleSearch."""
        return self._newscatcher_search_results(
            query,
            countries=self.c,
            lang=self.hl,
            page_size=self.ps,
            search_type=self.type,
            **kwargs,
        )

    def run(self, query: str, **kwargs: Any) -> str:
        """Run query through GoogleSearch and parse result."""
        results = self._newscatcher_search_results(
            query,
            countries=self.c,
            lang=self.hl,
            page_size=self.ps,
            search_type=self.type,
            **kwargs,
        )

        return self._parse_results(results)

    async def aresults(self, query: str, **kwargs: Any) -> Dict:
        """Run query through GoogleSearch."""
        results = await self._async_newscatcher_search_results(
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
        results = await self._async_newscatcher_search_results(
            query,
            countries=self.c,
            lang=self.hl,
            page_size=self.ps,
            search_type=self.type,
            **kwargs,
        )

        return self._parse_results(results)

    def _parse_results(self, results: dict) -> str:
        if results.get("status") == "error":
            raise ValueError(f"Got error from Newscatcher: {res.get('message')}")
        
        if results.get("status") != "ok":
            return "No good newscatcher results was found"
        
        articles = results.get("articles")
        
        if len(articles) == 0:
            return "No good newscatcher results was found"
        
        snippets = []
        
        for article in articles:
            title = article.get("title")
            author = article.get("author")
            published_date = article.get("published_date")
            excerpt = article.get("excerpt")
            summary = article.get("summary")
            link = article.get("link")

            snippet = (
                f"title: {title}\n"
                f"author: {author}\n"
                f"Published date: {published_date}\n"
                f"Excerpt: {excerpt}\n"
                f"Summary: {summary}\n"
                f"Link: {link}"
            )
                
            snippets.append(snippet)

        return " ".join(snippets)

    def _newscatcher_search_results(
        self, search_term: str, search_type: str = "search", **kwargs: Any
    ) -> dict:

        headers = {
            "X-API-KEY": self.newscatcher_api_key or "",
            "Content-Type": "application/json",
        }
        params = {
            "q": search_term,
            "lang":"en",
            "sort_by":"relevancy",
            "page":"1",
            **{key: value for key, value in kwargs.items() if value is not None},
        }
        response = requests.request(
            "GET", f"https://api.newscatcherapi.com/v2/{search_type}", headers=headers, params=params
        )
        response.raise_for_status()
        search_results = response.json()
        return search_results

    async def _async_newscatcher_search_results(
        self, search_term: str, search_type: str = "search", **kwargs: Any
    ) -> dict:
        headers = {
            "X-API-KEY": self.newscatcher_api_key or "",
            "Content-Type": "application/json",
        }
        url = f"https://api.newscatcherapi.com/v2/{search_type}"
        params = {
            "q": search_term,
            "lang":"en",
            "sort_by":"relevancy",
            "page":"1",
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






