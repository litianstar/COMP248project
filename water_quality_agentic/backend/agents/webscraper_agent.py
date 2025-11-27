# backend/agents/webscraper_agent.py
# WebSearcher / WebScraper Agent：这里先返回模拟数据
# WebSearcher / WebScraper Agent: returns mocked data for demo

class WebScraperAgent:
    def __init__(self):
        pass

    def fetch(self, query: str) -> str:
        """
        实际项目中可以用 requests 抓取网页。
        For prototype we just return a mocked snippet.
        """
        # 这里硬编码一个“最近新闻”的假数据 / Hard-coded fake "recent news"
        snippet = (
            "Recent online article (mocked): In 2025, environmental agencies reported "
            "that nitrate levels in some parts of Lake Ontario remained below WHO safe "
            "limits, but localized spikes occurred after heavy agricultural runoff events."
        )
        return snippet