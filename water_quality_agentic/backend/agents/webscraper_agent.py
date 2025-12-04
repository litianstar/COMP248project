# backend/agents/webscraper_agent.py
# WebScraper Agent: uses LLM to simulate fresh web knowledge (safe for demo)

import os
from mistralai import Mistral

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "vPWl25nWDSm6GP0IlDrSDJCC3fBvBH8v")
MISTRAL_MODEL_NAME = "mistral-small-latest"

class WebScraperAgent:
    """
    这个版本不做真实爬虫，而是调用 LLM 生成“模拟但合理的最新网络信息”
    更适合课堂作业：易运行、无爬虫风险、结果稳定。
    This version uses LLM to simulate “latest web info”, not real scraping.
    """

    def __init__(self):
        if not MISTRAL_API_KEY or MISTRAL_API_KEY == "YOUR_MISTRAL_KEY_HERE":
            raise ValueError("MISTRAL_API_KEY is not set.")
        self.client = Mistral(api_key=MISTRAL_API_KEY)

    def fetch(self, query: str) -> str:
        """
        使用 LLM “模拟” web 结果，避免真实爬虫不稳定。
        Use LLM to create a pseudo-web snippet relevant to the query.
        """

        prompt = f"""
        You are a Web Data Simulation Agent.

        Given the user question:
        {query}

        Generate a short paragraph (~60–100 words) summarizing what a 
        “recent credible online environmental news article or official report”
        *might* say about this topic around 2024–2025.

        Requirements:
        - Should sound realistic but not claim false facts
        - Must be generic but relevant
        - Do NOT fabricate specific URLs or fake organizations
        - Provide English only
        """

        response = self.client.chat.complete(
            model=MISTRAL_MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

        # return response.choices[0].message["content"]