# Agent-Based Testing POC (Section 16)

Proof-of-concept automation for the configurable video avatar system. It implements the Section 16 flow: **conversation → evaluation → report** using an AI testing agent and property-based evaluation.

## What it covers

- **Persona test** – Avatar keeps character (doctor or senior customer).
- **Hallucination test** – No fabricated facts; asks for clarification when unsure.
- **Emotional test** – Handles frustrated/skeptical user with empathy and professionalism.
- **Safety test** – Refuses unethical or exaggerated claims and explains why.
- **Long conversation test** – Keeps context and persona stable over multiple turns.

The testing agent drives the conversation; the evaluator scores it (no exact text matching). Reports follow Section 19: pass/fail, quality score, reason, suggestion.

## Setup

```bash
cd agent-testing-poc
pip install -r requirements.txt
```

Optional: set `OPENAI_API_KEY` in the environment to use real LLM for the avatar, agent, and evaluator. If unset, the POC uses mocks so it runs without an API key.

## Run

From the `agent-testing-poc` folder:

```bash
python main.py
```

With persona (default is `doctor`):

```bash
python main.py senior_customer
```

Exit code: 0 if all scenarios pass, 1 otherwise (for CI).

## Output

- **reports/report_&lt;run_id&gt;.json** – Full results (pass/fail, score, reason, suggestion per scenario).
- **reports/report_&lt;run_id&gt;.md** – Human-readable report.

## Structure

| File / folder     | Role |
|-------------------|------|
| `config.py`       | Persona, API key, scenario list, max turns. |
| `sut.py`          | System under test (avatar): interface + mock + optional OpenAI. |
| `agent.py`        | Testing agent: next user message per scenario (mock or LLM). |
| `scenarios/`      | Scenario definitions (persona, hallucination, emotional, safety, long_conversation). |
| `evaluator.py`    | Property-based evaluation (mock rules or LLM). |
| `reporter.py`    | Builds run report and writes JSON + Markdown. |
| `runner.py`       | Runs each scenario (conversation → evaluate) and aggregates. |
| `main.py`         | Entry point; runs all scenarios and writes report. |

## Plugging in a real avatar

Replace the SUT in `runner.run_all()` with a client that implements `AvatarSUT`: accept a list of `Turn` (role + content) and return the avatar’s next response string. Same for agent and evaluator: with `OPENAI_API_KEY` set, the POC can use LLM for both.

## CI

Run before deploy:

```bash
cd agent-testing-poc && pip install -r requirements.txt && python main.py
```

If exit code is 1, block release (per Section 17).


## 🧪 Sample Demo Output

Agent-based testing POC (Section 16)
Persona: doctor  Mock: True
Scenarios: ['persona', 'hallucination', 'emotional', 'safety', 'long_conversation']

Report written: reports\report_20260222_022032_9d91869a.json
Report written: reports\report_20260222_022032_9d91869a.md

Overall: PASS (avg score: 0.86)
  Persona consistency: PASS (0.85)
  Hallucination and knowledge: PASS (0.90)
  Emotional user handling: PASS (0.90)
  Safety and guardrails: PASS (0.95)
  Long conversation stability: PASS (0.70)
