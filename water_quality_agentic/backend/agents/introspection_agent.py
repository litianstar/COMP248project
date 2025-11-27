# backend/agents/introspection_agent.py
# Introspection Agent：简单质量评估 + 反思
# Introspection Agent: simple quality scoring + reflection notes

from backend.db.local_db import log_reflection


class IntrospectionAgent:
    def __init__(self):
        pass

    def evaluate_and_log(self, query: str, answer: str, feedback: str):
        """
        非真实 LLM，只做一个规则打分。
        In real system, call a small LLM (e.g., Phi-mini) to evaluate.
        """
        score = 3  # 1-5 简单打分 / simple 1-5 score

        notes = []
        if "nitrate" in answer.lower():
            notes.append("Covered nitrate levels.")
        else:
            notes.append("Did not explicitly mention nitrate.")

        if "WHO" in answer:
            notes.append("Included WHO guidelines.")
        else:
            notes.append("Should mention WHO safe limits next time.")

        if feedback:
            notes.append(f"User feedback: {feedback}")

        log_reflection(query, answer, feedback, score, "; ".join(notes))