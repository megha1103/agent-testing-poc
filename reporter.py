"""Report generation: Section 19 style (pass/fail, score, reason, suggestion)."""
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

@dataclass
class ScenarioResult:
    scenario_id: str
    scenario_name: str
    passed: bool
    score: float
    reason: str
    suggestion: str
    turn_count: int = 0
    error: str | None = None

@dataclass
class RunReport:
    run_id: str
    timestamp: str
    persona: str
    scenarios_run: list[str] = field(default_factory=list)
    results: list[ScenarioResult] = field(default_factory=list)
    overall_passed: bool = True
    total_score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "persona": self.persona,
            "scenarios_run": self.scenarios_run,
            "overall_passed": self.overall_passed,
            "total_score": round(self.total_score, 2),
            "results": [
                {
                    "scenario_id": r.scenario_id,
                    "scenario_name": r.scenario_name,
                    "passed": r.passed,
                    "score": r.score,
                    "reason": r.reason,
                    "suggestion": r.suggestion,
                    "turn_count": r.turn_count,
                    "error": r.error,
                }
                for r in self.results
            ],
        }

    def to_markdown(self) -> str:
        lines = [
            "# Agent-based testing report",
            "",
            f"**Run ID:** {self.run_id}  \n**Time:** {self.timestamp}  \n**Persona:** {self.persona}",
            "",
            f"**Overall:** {'PASS' if self.overall_passed else 'FAIL'}  \n**Average score:** {self.total_score:.2f}",
            "",
            "---",
            "",
            "## Results by scenario",
            "",
        ]
        for r in self.results:
            status = "PASS" if r.passed else "FAIL"
            lines.append(f"### {r.scenario_name} — {status} (score: {r.score:.2f})")
            lines.append("")
            lines.append(f"- **Reason:** {r.reason}")
            lines.append(f"- **Suggestion:** {r.suggestion}")
            if r.turn_count:
                lines.append(f"- **Turns:** {r.turn_count}")
            if r.error:
                lines.append(f"- **Error:** {r.error}")
            lines.append("")
        return "\n".join(lines)

def write_report(report: RunReport, report_dir: str) -> tuple[str, str]:
    """Write JSON and Markdown reports; return paths."""
    os.makedirs(report_dir, exist_ok=True)
    base = f"report_{report.run_id}"
    json_path = os.path.join(report_dir, f"{base}.json")
    md_path = os.path.join(report_dir, f"{base}.md")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report.to_dict(), f, indent=2)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report.to_markdown())
    return json_path, md_path
