"""Runner: conversation -> evaluation -> report (Section 16 flow)."""
import uuid
from datetime import datetime

from config import Config
from evaluator import Evaluator, EvalResult
from reporter import RunReport, ScenarioResult, write_report
from scenarios.definitions import ScenarioDef, SCENARIOS, get_scenario
from sut import AvatarSUT, Turn, MockAvatarSUT, OpenAIAvatarSUT
from agent import TestingAgent, AgentResult

def run_conversation(
    sut: AvatarSUT,
    agent: TestingAgent,
    scenario: ScenarioDef,
    max_turns: int,
) -> list[Turn]:
    """Run a single scenario: agent and avatar exchange turns until done or max_turns."""
    conversation: list[Turn] = []
    sut.reset()

    for turn_index in range(max_turns):
        agent_result = agent.next_message(scenario, conversation, turn_index, max_turns)
        user_msg = agent_result.message
        conversation.append(Turn(role="user", content=user_msg))

        avatar_msg = sut.respond(conversation)
        conversation.append(Turn(role="assistant", content=avatar_msg))

        if agent_result.done:
            break

    return conversation

def run_all(config: Config) -> RunReport:
    """Run all configured scenarios and build report."""
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:8]
    timestamp = datetime.now().isoformat()

    if config.use_mock:
        sut: AvatarSUT = MockAvatarSUT(persona=config.persona)
    else:
        sut = OpenAIAvatarSUT(
            api_key=config.api_key,
            system_prompt=config.avatar_context(),
        )

    agent = TestingAgent(use_mock=config.use_mock, api_key=config.api_key)
    evaluator = Evaluator(use_mock=config.use_mock, api_key=config.api_key)

    results: list[ScenarioResult] = []
    scenario_ids = [s for s in config.scenarios if s in SCENARIOS]

    for scenario_id in scenario_ids:
        scenario = get_scenario(scenario_id)
        if not scenario:
            continue
        try:
            conversation = run_conversation(
                sut=sut,
                agent=agent,
                scenario=scenario,
                max_turns=config.max_turns_per_scenario,
            )
            eval_result: EvalResult = evaluator.evaluate(scenario, conversation)
            turn_count = len([t for t in conversation if t.role == "user"])
            results.append(
                ScenarioResult(
                    scenario_id=scenario.id,
                    scenario_name=scenario.name,
                    passed=eval_result.passed,
                    score=eval_result.score,
                    reason=eval_result.reason,
                    suggestion=eval_result.suggestion,
                    turn_count=turn_count,
                )
            )
        except Exception as e:
            results.append(
                ScenarioResult(
                    scenario_id=scenario_id,
                    scenario_name=scenario_id.replace("_", " ").title(),
                    passed=False,
                    score=0.0,
                    reason="",
                    suggestion="Fix the error and re-run.",
                    error=str(e),
                )
            )

    total_score = sum(r.score for r in results) / len(results) if results else 0.0
    overall_passed = all(r.passed for r in results)

    report = RunReport(
        run_id=run_id,
        timestamp=timestamp,
        persona=config.persona,
        scenarios_run=scenario_ids,
        results=results,
        overall_passed=overall_passed,
        total_score=total_score,
    )
    return report
