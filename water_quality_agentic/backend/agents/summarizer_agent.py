# backend/agents/summarizer_agent.py

class SummarizerAgent:
    def __init__(self):
        pass

    def _build_conclusion(self, plan: dict | None) -> str:
        """
        根据 Planner 给的 plan，生成更合理的结论模板。
        Build a simple conclusion template based on topic and focus.
        """
        topic = (plan or {}).get("topic", "general")
        focus = (plan or {}).get("focus", "assessment")

        if topic == "heavy_metal" and focus == "causes":
            return (
                "For rural groundwater, the main risk factors for heavy metal pollution "
                "typically include: (1) agricultural chemicals and manure mismanagement, "
                "especially fertilizers or pesticides that contain cadmium or arsenic; "
                "(2) runoff and seepage from mining activities or waste rock piles; "
                "and (3) industrial discharge and corrosion of old pipelines.\n"
                "在农村地下水中，重金属污染的主要风险因素通常包括："
                "（1）农业化肥和农药等含镉、砷等重金属的投入品管理不当；"
                "（2）矿区及废石堆的渗漏和径流；"
                "（3）工业排放及老旧管网腐蚀。"
            )

        if topic == "nitrate":
            return (
                "Based on typical nitrate studies and guideline values, nitrate levels "
                "are mainly affected by agricultural fertilizer use, livestock manure, "
                "and wastewater leakage. Long term monitoring and local sampling are "
                "important to keep levels within safe limits.\n"
                "结合常见的硝酸盐研究和标准值，硝酸盐水平主要受农业施肥、畜禽粪便"
                "以及污水渗漏的影响。要保持在安全范围内，需要长期监测和本地取样。"
            )

        # fallback 一般水质结论
        return (
            "Overall, multiple environmental and human activities interact to shape "
            "local water quality. A combination of monitoring, source control and "
            "community awareness is required to manage long-term risks.\n"
            "总体来说，多种环境和人类活动共同影响当地水质，需要结合监测、源头控制"
            "以及社区意识提升，才能在长期内有效管理风险。"
        )

    def summarize(self, query: str, inhouse_text: str, web_text: str, plan=None) -> str:
        """
        In real system you call an LLM; here we just build a structured answer.
        """
        conclusion = self._build_conclusion(plan)

        summary_parts = [
            "Question / 问题:",
            query,
            "",
            "1) Internal findings / 内部文档发现:",
            inhouse_text[:600] + ("..." if len(inhouse_text) > 600 else ""),
            "",
            "2) Recent web evidence / 最新网络证据(模拟):",
            web_text,
            "",
            "3) Preliminary conclusion / 初步结论:",
            conclusion,
        ]
        return "\n".join(summary_parts)