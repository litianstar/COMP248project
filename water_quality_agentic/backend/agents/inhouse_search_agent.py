# backend/agents/inhouse_search_agent.py
# InHouseSearch Agent：本地水质语料检索（升级版）
# InHouseSearch Agent: smarter keyword-based routing over local water-quality corpus

from pathlib import Path


class InHouseSearchAgent:
    def __init__(self):
        """
        初始化本地语料库。
        必选文件：
          - who_water_guidelines.txt
          - ontario_lake_report_2025.txt

        可选文件（建议你后面逐步补充）：
          - heavy_metal_guidelines.txt
          - phosphorus_nutrients_notes.txt
          - groundwater_quality_notes.txt
          - microbial_ecoli_notes.txt
          - ecosystem_health_notes.txt
          - general_background.txt
        如果某个文件不存在，不会报错，只是对应的内容不会被加载。
        """
        base = Path(__file__).resolve().parents[2] / "data" / "inhouse_corpus"

        self.docs = {}

        def safe_load(key: str, filename: str):
            path = base / filename
            if path.exists():
                self.docs[key] = path.read_text(encoding="utf-8")

        # --- 必备基础文档 ---
        safe_load("who", "who_water_guidelines.txt")
        safe_load("ontario", "ontario_lake_report_2025.txt")

        # --- 建议增加的扩展语料 ---
        safe_load("heavy", "heavy_metal_guidelines.txt")
        safe_load("phosphorus", "phosphorus_nutrients_notes.txt")
        safe_load("groundwater", "groundwater_quality_notes.txt")
        safe_load("microbial", "microbial_ecoli_notes.txt")
        safe_load("ecosystem", "ecosystem_health_notes.txt")
        safe_load("background", "general_background.txt")

    def search(self, query: str) -> str:
        """
        非向量检索的简化版：根据关键词和主题，拼接合适的文档内容。
        Simple keyword-based routing: choose relevant internal docs based on query text.
        """
        q = query.lower()
        chunks = []

        # --- 1) Nitrate / nutrients 相关 ---
        if any(k in q for k in ["nitrate", "no3", "nitrogen", "nutrient", "fertilizer", "肥料", "营养盐"]):
            if "who" in self.docs:
                chunks.append("【WHO Drinking Water Guidelines】\n" + self.docs["who"])
            if "ontario" in self.docs:
                chunks.append("【Ontario Lake 2025 Report】\n" + self.docs["ontario"])

        # --- 2) 磷 / Phosphorus 相关 ---
        if any(k in q for k in ["phosphorus", "phosphate", "磷"]):
            if "phosphorus" in self.docs:
                chunks.append("【Phosphorus & Nutrient Notes】\n" + self.docs["phosphorus"])
            # 没有专门的磷文件时，可以至少给安大略报告
            elif "ontario" in self.docs and "【Ontario Lake 2025 Report】" not in "".join(chunks):
                chunks.append("【Ontario Lake 2025 Report】\n" + self.docs["ontario"])

        # --- 3) 重金属 / Heavy metals 相关（cadmium, arsenic, lead, mercury）---
        if any(k in q for k in ["cadmium", "arsenic", "lead", "mercury", "heavy metal", "重金属", "镉", "砷", "铅"]):
            if "heavy" in self.docs:
                chunks.append("【WHO Heavy Metal Guidelines】\n" + self.docs["heavy"])
            # 如果没有单独 heavy 文件，至少给 WHO 总指南
            elif "who" in self.docs and "【WHO Drinking Water Guidelines】" not in "".join(chunks):
                chunks.append("【WHO Drinking Water Guidelines】\n" + self.docs["who"])

        # --- 4) 地下水 / 农村水井 Groundwater / wells ---
        if any(k in q for k in ["groundwater", "well", "rural well", "地下水", "水井", "农村"]):
            if "groundwater" in self.docs:
                chunks.append("【Rural Groundwater Notes】\n" + self.docs["groundwater"])

        # --- 5) 微生物 / E.coli 等 ---
        if any(k in q for k in ["e. coli", "ecoli", "bacteria", "microbial", "大肠杆菌", "细菌"]):
            if "microbial" in self.docs:
                chunks.append("【Microbial & E. coli Notes】\n" + self.docs["microbial"])
            # 安大略报告里通常也包含微生物监测
            elif "ontario" in self.docs and "【Ontario Lake 2025 Report】" not in "".join(chunks):
                chunks.append("【Ontario Lake 2025 Report】\n" + self.docs["ontario"])

        # --- 6) 生态健康 / ecosystem health ---
        if any(k in q for k in ["ecosystem health", "生态健康", "fish", "algae", "eutrophication", "富营养化"]):
            if "ecosystem" in self.docs:
                chunks.append("【Ecosystem Health Notes】\n" + self.docs["ecosystem"])

        # --- 7) 如果出现 “Lake Ontario” 或 “Ontario” 但上面没触发 ---
        if ("lake ontario" in q or "ontario" in q) and "ontario" in self.docs:
            # 避免重复添加
            if "【Ontario Lake 2025 Report】" not in "".join(chunks):
                chunks.append("【Ontario Lake 2025 Report】\n" + self.docs["ontario"])

        # --- 8) 如果出现 WHO / safe limit 等 ---
        if any(k in q for k in ["who", "safe limit", "guideline", "标准", "指南"]):
            if "who" in self.docs and "【WHO Drinking Water Guidelines】" not in "".join(chunks):
                chunks.append("【WHO Drinking Water Guidelines】\n" + self.docs["who"])

        # --- 9) 如果上面都没命中，给一个通用背景 ---
        if not chunks:
            if "background" in self.docs:
                chunks.append("【General Background】\n" + self.docs["background"])
            else:
                chunks.append(
                    "General note: internal corpus contains WHO limits, Ontario lake data, "
                    "and optional notes on heavy metals, groundwater, nutrients, and ecosystem health."
                )

        return "\n\n".join(chunks)