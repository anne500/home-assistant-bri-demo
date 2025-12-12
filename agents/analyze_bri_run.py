import pathlib

LOG_FILES = ["build.log", "test.log", "release.log", "policy.log"]

def parse_metrics(lines):
    metrics = {}
    for line in lines:
        line = line.strip()
        if line.startswith("METRIC "):
            parts = line.split()
            fields = {}
            for part in parts[1:]:
                if "=" in part:
                    k, v = part.split("=", 1)
                    fields[k] = v
            key = "{}.{}".format(fields.get("job", "unknown"), fields.get("key", "unknown"))
            metrics[key] = fields.get("value", "")
    return metrics

def main():
    metrics = {}
    for name in LOG_FILES:
        p = pathlib.Path(name)
        if p.exists():
            m = parse_metrics(p.read_text().splitlines())
            metrics.update(m)

    print("=== BRI Agent Analysis (Placeholder) ===")
    for k, v in metrics.items():
        print(f"{k}: {v}")

    tests_total = metrics.get("test_agent.tests_total", "0")
    if tests_total in ("0", "") or tests_total.startswith("tests/"):
        print("\n[Agent Suggestion] Only 1 trivial test detected. Consider adding more scenario-based tests for the custom components.")
    else:
        print("\n[Agent Suggestion] Test suite size looks non-trivial; next step is to analyze coverage and failure patterns.")

if __name__ == "__main__":
    main()
