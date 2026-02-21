"""CLI demo: run one scenario with full conversation and evaluation printed."""
import sys
from config import Config
from sut import Turn, MockAvatarSUT, OpenAIAvatarSUT
from agent import TestingAgent
from evaluator import Evaluator
from scenarios.definitions import SCENARIOS, get_scenario

def main() -> int:
    config = Config()
    scenario_id = "persona"
    if len(sys.argv) > 1 and sys.argv[1] in SCENARIOS:
        scenario_id = sys.argv[1]
    if len(sys.argv) > 2:
        config.persona = sys.argv[2]

    scenario = get_scenario(scenario_id)
    if not scenario:
        print("Unknown scenario. Use: persona | hallucination | emotional | safety | long_conversation")
        return 1

    print("=" * 60)
    print("AGENT-BASED TESTING DEMO")
    print("=" * 60)
    print(f"Persona: {config.persona}")
    print(f"Scenario: {scenario.name}")
    print(f"Mock mode: {config.use_mock}")
    print()
    print("Scenario instruction (testing agent):")
    print(f"  {scenario.agent_instruction[:200]}...")
    print()
    print("-" * 60)
    print("CONVERSATION")
    print("-" * 60)

    if config.use_mock:
        sut = MockAvatarSUT(persona=config.persona)
    else:
        sut = OpenAIAvatarSUT(api_key=config.api_key, system_prompt=config.avatar_context())
    agent = TestingAgent(use_mock=config.use_mock, api_key=config.api_key)
    max_turns = config.max_turns_per_scenario

    conversation: list[Turn] = []
    sut.reset()

    for turn_index in range(max_turns):
        agent_result = agent.next_message(scenario, conversation, turn_index, max_turns)
        user_msg = agent_result.message
        conversation.append(Turn(role="user", content=user_msg))
        print(f"\n  User: {user_msg}")

        avatar_msg = sut.respond(conversation)
        conversation.append(Turn(role="assistant", content=avatar_msg))
        print(f"  Avatar: {avatar_msg}")

        if agent_result.done:
            break

    print()
    print("-" * 60)
    turn_objs = [Turn(role=r, content=c) for r, c in conversation]
    print("EVALUATION")
    print("-" * 60)

    evaluator = Evaluator(use_mock=config.use_mock, api_key=config.api_key)
    result = evaluator.evaluate(scenario, conversation)

    print(f"  Passed: {result.passed}")
    print(f"  Score:  {result.score:.2f}")
    print(f"  Reason: {result.reason}")
    print(f"  Suggestion: {result.suggestion}")
    print()
    print("=" * 60)
    return 0 if result.passed else 1

if __name__ == "__main__":
    sys.exit(main())
