# backend/agents/planner_agent.py
# Planner Agent：协调其它 Agent，并给出调试信息
# Planner Agent: orchestrates other agents and returns debug info

import re
from backend.agents.inhouse_search_agent import InHouseSearchAgent
from backend.agents.webscraper_agent import WebScraperAgent
from backend.agents.summarizer_agent import SummarizerAgent


class PlannerAgent:
    """
    简化版 Planner：
    - 负责对用户水污染/水质问题做关键词级“意图分类”
    - 决定是否需要 Web 搜索（根据时间、latest、recent 等）
    - 调用 InHouseSearch + WebScraper + Summarizer
    - 返回最终答案 + 调试信息

    Simple planner:
    - Performs lightweight intent classification based on keywords
    - Decides whether web search is needed
    - Calls in-house search, web scraper and summarizer
    - Returns final answer plus debug info
    """

    def __init__(self):
        self.inhouse_agent = InHouseSearchAgent()
        self.web_agent = WebScraperAgent()
        self.summarizer = SummarizerAgent()

    # ---------- internal helpers / 内部辅助函数 ----------

    def _classify_query(self, query: str) -> dict:
        """
        基于关键词对问题做一个粗粒度分类：
        - topic: nitrate / heavy_metal / microbial / general
        - focus: causes / mitigation / assessment
        - need_web: 是否需要查最新信息

        A simple keyword-based classification.
        """
        q = query.lower()

        # 1) topic 主题分类
        if any(k in q for k in ["nitrate", "nitrite", "nutrient"]):
            topic = "nitrate"
        elif any(k in q for k in ["heavy metal", "cadmium", "lead", "mercury", "arsenic"]):
            topic = "heavy_metal"
        elif any(k in q for k in ["bacteria", "e. coli", "microbial", "pathogen"]):
            topic = "microbial"
        else:
            topic = "general"

        # 2) focus 关注点：风险因素 / 缓解措施 / 评估
        if any(k in q for k in ["risk factor", "cause", "source"]):
            focus = "causes"
        elif any(k in q for k in ["solution", "mitigation", "reduce", "control"]):
            focus = "mitigation"
        else:
            focus = "assessment"

        # 3) 是否需要 time-sensitive / 最新信息
        need_web = False
        if re.search(r"202[0-9]", q):
            need_web = True
        if any(k in q for k in ["recent", "latest", "current", "up to date"]):
            need_web = True

        plan = {
            "topic": topic,
            "focus": focus,
            "need_web": need_web,
            "raw_query": query,
        }
        return plan

    # ---------- public API / 对外接口 ----------

    def handle_query(self, query: str):
        """
        主入口：
        - 分析问题 → 生成 plan
        - 调用 InHouseSearch
        - 若 need_web=True 则调用 WebScraper
        - 调用 Summarizer 生成统一回答
        - 返回 (answer, debug_info)
        """
        plan = self._classify_query(query)

        debug_info = {
            "plan": plan,
            "called_agents": [],
            "inhouse_preview": "",
            "web_preview": "",
        }

        # 1) 总是调用内部水质语料（WHO + Ontario 报告）
        inhouse_result = self.inhouse_agent.search(query)
        debug_info["called_agents"].append("InHouseSearchAgent")
        debug_info["inhouse_preview"] = inhouse_result[:300]

        # 2) 根据需要决定是否调用 Web 搜索
        if plan["need_web"]:
            web_result = self.web_agent.fetch(query)
            debug_info["called_agents"].append("WebScraperAgent")
        else:
            web_result = "Web search not triggered for this query."
        debug_info["web_preview"] = web_result[:300]

        # 3) 调用 Summarizer 汇总，顺便把 plan 传进去（便于更合理的结论）
        answer = self.summarizer.summarize(query, inhouse_result, web_result, plan=plan)
        debug_info["final_answer_preview"] = answer[:300]

        return answer, debug_info