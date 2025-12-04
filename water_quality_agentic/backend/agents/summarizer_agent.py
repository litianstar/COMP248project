# backend/agents/summarizer_agent.py
# Summarizer Agent：使用 Mistral LLM 生成真实摘要
# Summarizer Agent: uses Mistral LLM to generate real summaries

import os
from mistralai import Mistral


# 从环境变量读取 API Key，避免写死在代码里
# Read API key from environment variable
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "vPWl25nWDSm6GP0IlDrSDJCC3fBvBH8v")
MISTRAL_MODEL_NAME = "mistral-small-latest"


class SummarizerAgent:
    def __init__(self):
        if not MISTRAL_API_KEY or MISTRAL_API_KEY == "YOUR_MISTRAL_KEY_HERE":
            raise ValueError(
                "MISTRAL_API_KEY is not set. Please export it in your environment."
            )
        self.client = Mistral(api_key=MISTRAL_API_KEY)

    def summarize(self, query: str, inhouse_text: str, web_text: str, plan=None) -> str:
        """
        使用真实 LLM 生成摘要：
        - 输入：用户问题、内部文档内容、web 内容、Planner 计划
        - 输出：中英文双语、结构化（水质背景 → 数据 → 风险 → 建议）
        Uses real LLM to generate a bilingual structured summary.
        """

        system_prompt = """
        You are a Water Pollution & Quality Summarization Agent.
        Your job is to:
        - merge internal water-quality documents and web content,
        - check consistency between internal and web evidence,
        - and produce a structured answer with this structure:
          1) Background
          2) Key water-quality data
          3) Risk analysis
          4) Recommendations
        The answer MUST be bilingual: English first, then Chinese translation.
        Be concise but informative, suitable for a research analyst.
        """

        user_prompt = f"""
        USER QUESTION:
        {query}

        PLANNER PLAN (topic, focus, need_web):
        {plan}

        INTERNAL DOCUMENTS (in-house corpus):
        {inhouse_text}

        WEB CONTENT (if any):
        {web_text}

        TASK:
        - Merge the above information.
        - Resolve or explain any conflicts between internal and web data.
        - Follow the required structure.
        - Output English + Chinese (each bullet point can have EN + CN).
        """

        response = self.client.chat.complete(
            model=MISTRAL_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content

        # return response.choices[0].message["content"]
    