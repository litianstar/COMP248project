# backend/api_server.py

from backend.db.local_db import init_db, log_query
from backend.agents.planner_agent import PlannerAgent
from backend.agents.introspection_agent import IntrospectionAgent

# 初始化数据库
init_db()

planner = PlannerAgent()
introspector = IntrospectionAgent()


def handle_query(query: str):
    """
    给前端调用的核心入口。
    返回：(answer, debug_info)
    """
    if not query.strip():
        return (
            "Please enter a non-empty question about water pollution or water quality.",
            {},
        )

    # 1) 调用 Planner 完成整个多智能体流程
    answer, debug_info = planner.handle_query(query)

    # 2) 记录查询和答案
    log_query(query, answer)

    return answer, debug_info


def submit_feedback(query: str, answer: str, feedback: str):
    """前端提交用户反馈，交给 Introspection Agent."""
    introspector.evaluate_and_log(query, answer, feedback)