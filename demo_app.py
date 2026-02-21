"""Web demo: run scenarios and see conversation + report in the browser."""
import streamlit as st
from config import Config
from sut import Turn, MockAvatarSUT, OpenAIAvatarSUT
from agent import TestingAgent
from evaluator import Evaluator
from scenarios.definitions import SCENARIOS, get_scenario
from reporter import RunReport, ScenarioResult, write_report
from runner import run_conversation, run_all

st.set_page_config(page_title="Agent Testing Demo", page_icon="🤖", layout="wide")

st.title("Agent-based testing demo")
st.caption("Section 16: conversation → evaluation → report")

persona = st.sidebar.selectbox("Persona", ["doctor", "senior_customer"], index=0)
scenario_ids = list(SCENARIOS.keys())
selected_scenarios = st.sidebar.multiselect(
    "Scenarios to run",
    scenario_ids,
    default=["persona", "safety"],
)
run_single = st.sidebar.checkbox("Demo single scenario (show each turn)", value=True)

config = Config()
config.persona = persona
config.scenarios = selected_scenarios if selected_scenarios else scenario_ids
config.use_mock = not bool(st.sidebar.text_input("OPENAI_API_KEY (optional)", type="password"))
if st.sidebar.text_input("OPENAI_API_KEY (optional)", type="password"):
    config.api_key = st.sidebar.text_input("OPENAI_API_KEY (optional)", type="password")
# Avoid storing key in session; keep mock if no key
import os
config.use_mock = not bool(os.getenv("OPENAI_API_KEY"))
config.api_key = os.getenv("OPENAI_API_KEY", "")

if run_single and selected_scenarios:
    scenario_id = selected_scenarios[0]
    scenario = get_scenario(scenario_id)
    if scenario:
        st.subheader(f"Scenario: {scenario.name}")
        st.write(scenario.agent_instruction[:300] + "..." if len(scenario.agent_instruction) > 300 else scenario.agent_instruction)

        if config.use_mock:
            sut = MockAvatarSUT(persona=config.persona)
        else:
            sut = OpenAIAvatarSUT(api_key=config.api_key, system_prompt=config.avatar_context())
        agent = TestingAgent(use_mock=config.use_mock, api_key=config.api_key)
        evaluator = Evaluator(use_mock=config.use_mock, api_key=config.api_key)

        conversation: list[Turn] = []
        sut.reset()
        max_turns = config.max_turns_per_scenario

        for turn_index in range(max_turns):
            agent_result = agent.next_message(scenario, conversation, turn_index, max_turns)
            user_msg = agent_result.message
            conversation.append(Turn(role="user", content=user_msg))
            avatar_msg = sut.respond(conversation)
            conversation.append(Turn(role="assistant", content=avatar_msg))

            with st.container():
                st.markdown("**User**")
                st.write(user_msg)
                st.markdown("**Avatar**")
                st.write(avatar_msg)
                st.divider()
            if agent_result.done:
                break

        result = evaluator.evaluate(scenario, conversation)
        st.subheader("Evaluation")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Passed", "Yes" if result.passed else "No")
            st.metric("Score", f"{result.score:.2f}")
        with col2:
            st.write("**Reason:**", result.reason)
            st.write("**Suggestion:**", result.suggestion)
else:
    st.subheader("Run all selected scenarios")
    if st.button("Run tests"):
        report = run_all(config)
        json_path, md_path = write_report(report, config.report_dir)
        st.success(f"Report saved: {md_path}")

        st.metric("Overall", "PASS" if report.overall_passed else "FAIL")
        st.metric("Average score", f"{report.total_score:.2f}")

        for r in report.results:
            with st.expander(f"{r.scenario_name} — {'PASS' if r.passed else 'FAIL'} ({r.score:.2f})"):
                st.write("**Reason:**", r.reason)
                st.write("**Suggestion:**", r.suggestion)
        st.download_button("Download report (Markdown)", open(md_path).read(), file_name=md_path.split("/")[-1].split("\\")[-1], mime="text/markdown")
