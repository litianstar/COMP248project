# backend/agents/planner_agent.py
# Planner Agent：使用 Mistral LLM 做任务规划，并协调其它 Agent
# Planner Agent: uses Mistral LLM to plan tasks and orchestrate agents

import os
import json
from mistralai import Mistral

from backend.agents.inhouse_search_agent import InHouseSearchAgent
from backend.agents.webscraper_agent import WebScraperAgent
from backend.agents.summarizer_agent import SummarizerAgent

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "vPWl25nWDSm6GP0IlDrSDJCC3fBvBH8v")
MISTRAL_MODEL_NAME = "mistral-small-latest"


class PlannerAgent:
    """
    新版 Planner：
    - 使用 Mistral LLM 对 query 做 task planning（主题/关注点/是否需要 web）
    - 再调用 InHouseSearch + WebScraper + Summarizer
    - 返回 answer 和 debug 信息（供前端展示）
    """

    def __init__(self):
        if not MISTRAL_API_KEY or MISTRAL_API_KEY == "YOUR_MISTRAL_KEY_HERE":
            raise ValueError(
                "MISTRAL_API_KEY is not set. Please export it in your environment."
            )
        self.llm = Mistral(api_key=MISTRAL_API_KEY)
        self.inhouse_agent = InHouseSearchAgent()
        self.web_agent = WebScraperAgent()
        self.summarizer = SummarizerAgent()

    # ---------- LLM 规划函数 ----------

    def _llm_plan(self, query: str) -> dict:
        """
        使用 LLM 分析用户问题，输出 JSON 格式的规划:
        {
          "topic": "nitrate" | "heavy_metal" | "microbial" | "general",
          "focus": "causes" | "mitigation" | "assessment",
          "need_web": true/false
        }
        """

        
        plan_prompt = f"""
        You are an Agentic AI Planner for a Water Pollution & Water Quality Intelligence System.

        Your task is to analyze the user query and produce a structured JSON plan with:

        1) topic  
        2) focus  
        3) need_web  (true/false)

        Follow the rules below *strictly*:

        ========================================
        ### 1. Topic classification  
        Choose EXACTLY one of the following topics:

        - "nitrate"
        - "phosphorus"
        - "heavy_metals"
        - "microbial"
        - "nutrients"
        - "ecosystem_health"
        - "groundwater"
        - "lake"
        - "mixed"        ← use this if multiple pollutants or topics appear
        - "general"      ← fallback if no specific pollutant is mentioned

        Examples:
        - If query mentions nitrate → "nitrate"
        - If query mentions cadmium, arsenic, lead → "heavy_metals"
        - If query mentions nitrate + phosphorus → "mixed"
        - If query mentions lake ecosystem health → "ecosystem_health"

        ========================================
        ### 2. Focus classification  
        Choose EXACTLY one focus:

        - "assessment"        ← evaluate current levels vs safety standards
        - "trend_analysis"    ← long-term changes, time trends
        - "comparison"        ← compare two pollutants or sources
        - "mitigation"        ← solutions, strategies, recommendations
        - "risk"              ← health or environmental impact
        - "origin"            ← sources of pollution
        - "prediction"        ← future projections or expected trends

        Examples:
        - “Is it safe?” → assessment  
        - “Long-term trends” → trend_analysis  
        - “Compare A and B” → comparison  
        - “How to reduce X?” → mitigation  
        - “What are the risks?” → risk  

        ========================================
        ### 3. need_web (true/false)
        Set to TRUE if:

        - Query mentions a specific year (e.g., 2024, 2025)
        - Or mentions "recent", "latest", "current", "up-to-date"
        - Or asks for evolving conditions, real-time trends
        Else FALSE.

        ========================================
        ### IMPORTANT RULES
        - If the query involves more than one pollutant or parameter → topic = "mixed"
        - If the query involves lake ecosystem impacts → topic = "ecosystem_health"
        - Return JSON only. Absolutely no explanation.

        ========================================
        User query:
        {query}
        """

        resp = self.llm.chat.complete(
            model=MISTRAL_MODEL_NAME,
            messages=[{"role": "user", "content": plan_prompt}],
        )

        # raw = resp.choices[0].message["content"]
        raw = resp.choices[0].message.content

        # 尝试解析 JSON，失败则回退为简单规则
        try:
            plan = json.loads(raw)
            # 保底：字段缺失时设置默认值
            plan.setdefault("topic", "general")
            plan.setdefault("focus", "assessment")
            plan.setdefault("need_web", True)
            return plan
        except Exception:
            # fallback：简单 keyword 规则，避免 demo 挂掉
            q = query.lower()
            if "nitrate" in q or "nutrient" in q:
                topic = "nitrate"
            elif any(k in q for k in ["heavy metal", "lead", "cadmium", "mercury", "arsenic"]):
                topic = "heavy_metal"
            elif any(k in q for k in ["bacteria", "e. coli", "microbial", "pathogen"]):
                topic = "microbial"
            else:
                topic = "general"

            if any(k in q for k in ["risk factor", "cause", "source"]):
                focus = "causes"
            elif any(k in q for k in ["solution", "mitigation", "reduce", "control"]):
                focus = "mitigation"
            else:
                focus = "assessment"

            need_web = any(
                kw in q for kw in ["2020", "2021", "2022", "2023", "2024", "2025", "latest", "current"]
            )

            return {"topic": topic, "focus": focus, "need_web": need_web}

    # ---------- 外部调用接口 ----------

    def handle_query(self, query: str):
        """
        对前端暴露的主函数：
        - 调用 LLM 规划
        - 调用 InHouse / Web / Summarizer
        - 返回 (answer, debug_info)
        """
        plan = self._llm_plan(query)

        debug_info = {
            "plan": plan,
            "called_agents": [],
            "inhouse_preview": "",
            "web_preview": "",
        }

        # 1) 内部检索
        inhouse = self.inhouse_agent.search(query)
        debug_info["called_agents"].append("InHouseSearchAgent")
        debug_info["inhouse_preview"] = inhouse[:300]

        # 2) 视情况决定是否查 Web
        if plan.get("need_web", True):
            web = self.web_agent.fetch(query)
            debug_info["called_agents"].append("WebScraperAgent")
        else:
            web = ""
        debug_info["web_preview"] = web[:300]

        # 3) Summarizer 生成最终答案（真实 LLM）
        answer = self.summarizer.summarize(
            query=query,
            inhouse_text=inhouse,
            web_text=web,
            plan=plan,
        )
        debug_info["final_answer_preview"] = answer[:300]

        return answer, debug_info