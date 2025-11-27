# frontend/streamlit_app.py

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from backend.api_server import handle_query, submit_feedback

st.set_page_config(page_title="Water Quality Agentic Demo", layout="wide")

st.title("Water Pollution & Quality Research Assistant")
st.write("Agentic AI Demo")

default_query = (
    "As a research analyst, I want to understand whether nitrate level "
    "in Lake Ontario in 2025 is within WHO safe limits."
)

query = st.text_area(
    "Enter your question ：",
    value=default_query,
    height=120,
)

if st.button("Run multi-agent analysis "):
    with st.spinner("Running planner and agents..."):
        answer, debug_info = handle_query(query)
    st.session_state["last_query"] = query
    st.session_state["last_answer"] = answer
    st.session_state["last_debug"] = debug_info

if "last_answer" in st.session_state:
    st.subheader("Answer ：")
    st.text_area(
        "System output ：",
        value=st.session_state["last_answer"],
        height=320,
    )

    # ====== 新增：调试信息展示 / Debug info ======
    st.subheader("Debug info ：")
    show_debug = st.checkbox("Show planner & agents debug ")

    if show_debug and "last_debug" in st.session_state:
        debug = st.session_state["last_debug"]

        st.markdown("**Planner plan ：**")
        st.json(debug.get("plan", {}))

        st.markdown("**Called agents ：**")
        st.write(", ".join(debug.get("called_agents", [])))

        st.markdown("**In-house search preview ：**")
        st.code(debug.get("inhouse_preview", ""), language="text")

        st.markdown("**Web search preview ：**")
        st.code(debug.get("web_preview", ""), language="text")

    # ====== 用户反馈 ======
    st.subheader("Feedback ：")
    feedback = st.text_input("Optional feedback ")
    if st.button("Submit feedback "):
        submit_feedback(
            st.session_state["last_query"],
            st.session_state["last_answer"],
            feedback,
        )
        st.success("Feedback recorded. ")