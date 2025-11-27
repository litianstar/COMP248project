# backend/agents/inhouse_search_agent.py
# InHouseSearch Agent：本地水质语料检索（伪实现）
# InHouseSearch Agent: search internal water-quality corpus (toy version)

from pathlib import Path


class InHouseSearchAgent:
    def __init__(self):
        base = Path(__file__).resolve().parents[2] / "data" / "inhouse_corpus"
        self.docs = {
            "who": (base / "who_water_guidelines.txt").read_text(encoding="utf-8"),
            "ontario": (base / "ontario_lake_report_2025.txt").read_text(
                encoding="utf-8"
            ),
        }

    def search(self, query: str) -> str:
        """
        非向量检索的简化版：根据关键词拼接文档片段。
        Simple keyword-based search instead of embeddings.
        """
        query_lower = query.lower()
        chunks = []

        if "who" in query_lower or "safe limit" in query_lower:
            chunks.append("【WHO Drinking Water Guidelines】\n" + self.docs["who"])

        if "ontario" in query_lower or "lake ontario" in query_lower:
            chunks.append("【Ontario Lake 2025 Report】\n" + self.docs["ontario"])

        if not chunks:
            # 默认给一点背景
            chunks.append(
                "General note: internal corpus contains WHO limits and Ontario lake data."
            )

        return "\n\n".join(chunks)