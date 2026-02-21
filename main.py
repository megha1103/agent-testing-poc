"""Entry point: run agent-based testing POC (Section 16)."""
import sys
from config import Config
from runner import run_all
from reporter import write_report

def main() -> int:
    config = Config()
    if len(sys.argv) > 1:
        config.persona = sys.argv[1]
    if "all" in sys.argv or "--all" in sys.argv:
        config.scenarios = list(config.scenarios)  # default already has all

    print("Agent-based testing POC (Section 16)")
    print(f"Persona: {config.persona}  Mock: {config.use_mock}")
    print(f"Scenarios: {config.scenarios}")
    print()

    report = run_all(config)

    json_path, md_path = write_report(report, config.report_dir)
    print(f"Report written: {json_path}")
    print(f"Report written: {md_path}")
    print()
    print(f"Overall: {'PASS' if report.overall_passed else 'FAIL'} (avg score: {report.total_score:.2f})")
    for r in report.results:
        status = "PASS" if r.passed else "FAIL"
        print(f"  {r.scenario_name}: {status} ({r.score:.2f})")

    return 0 if report.overall_passed else 1

if __name__ == "__main__":
    sys.exit(main())
