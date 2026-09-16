from pathlib import Path
import csv
import math
import statistics

ROOT = Path(__file__).resolve().parents[1]
CSV_FILE = ROOT / "results" / "per_item.csv"
MODEL = "qwen2.5-coder:3b"

with CSV_FILE.open("r", encoding="utf-8", newline="") as file:
    rows = [
        row for row in csv.DictReader(file)
        if row["model"] == MODEL and row["split"] == "test"
    ]

if len(rows) != 54:
    raise ValueError(f"Expected 54 Ollama test rows, found {len(rows)}")

latencies = sorted(float(row["latency_ms"]) / 1000 for row in rows)
p50 = statistics.median(latencies)
p95 = latencies[math.ceil(0.95 * len(latencies)) - 1]

output_tokens = sum(int(row["output_tokens"]) for row in rows)
eval_seconds = sum(int(row["eval_duration_ns"]) for row in rows) / 1_000_000_000
tokens_per_second = output_tokens / eval_seconds

correct = sum(int(row["correct"]) for row in rows)

print(f"Accuracy: {correct}/54 ({correct / 54:.1%})")
print(f"p50 latency: {p50:.2f} seconds")
print(f"p95 latency: {p95:.2f} seconds")
print(f"Output speed: {tokens_per_second:.1f} tokens/second")