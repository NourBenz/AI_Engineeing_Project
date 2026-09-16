from pathlib import Path
from urllib import request, error
import csv
import json
import time

from score import load_items, score_item


ROOT = Path(__file__).resolve().parents[1]
PROMPT_FILE = ROOT / "src" / "prompt.txt"
RESULTS_FILE = ROOT / "results" / "per_item.csv"

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5-coder:3b"

FIELDNAMES = [
    "item_id", "split", "difficulty", "model",
    "correct", "error", "latency_ms",
    "prompt_tokens", "output_tokens", "eval_duration_ns",
    "done_reason", "generated_sql",
]


def clean_sql(text):
    sql = text.strip()
    if sql.startswith("```"):
        lines = sql.splitlines()
        if len(lines) >= 2 and lines[-1].strip() == "```":
            sql = "\n".join(lines[1:-1]).strip()
    return sql


def ask_ollama(prompt):
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {
            "temperature": 0,
            "num_predict": 256,
            "num_ctx": 4096,
            "seed": 496,
        },
    }

    req = request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    start = time.perf_counter()
    with request.urlopen(req, timeout=120) as response:
        result = json.load(response)
    latency_ms = (time.perf_counter() - start) * 1000

    return result, latency_ms


def save_rows(new_rows):
    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    existing_rows = []

    if RESULTS_FILE.exists() and RESULTS_FILE.stat().st_size > 0:
        with RESULTS_FILE.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            if reader.fieldnames != FIELDNAMES:
                raise ValueError(
                    "results/per_item.csv has different columns. "
                    "Check it before replacing any results."
                )
            existing_rows = [
                row for row in reader if row["model"] != MODEL
            ]

    with RESULTS_FILE.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(existing_rows + new_rows)


def main():
    template = PROMPT_FILE.read_text(encoding="utf-8")
    if "{question}" not in template:
        raise ValueError("src/prompt.txt must contain {question}")

    test_items = [
        item for item in load_items() if item["split"] == "test"
    ]
    if len(test_items) < 50:
        raise ValueError(f"Expected at least 50 test items; found {len(test_items)}")

    print(f"Running {len(test_items)} test questions with {MODEL}")
    rows = []

    for item in test_items:
        prompt = template.replace("{question}", item["question"])
        start = time.perf_counter()

        try:
            result, latency_ms = ask_ollama(prompt)
            sql = clean_sql(result["message"]["content"])
            score = score_item(item, sql)

            row = {
                "item_id": item["id"],
                "split": item["split"],
                "difficulty": item["difficulty"],
                "model": MODEL,
                "correct": int(score["correct"]),
                "error": score["error"] or "",
                "latency_ms": round(latency_ms, 2),
                "prompt_tokens": result.get("prompt_eval_count", ""),
                "output_tokens": result.get("eval_count", ""),
                "eval_duration_ns": result.get("eval_duration", ""),
                "done_reason": result.get("done_reason", ""),
                "generated_sql": sql,
            }

        except (error.URLError, TimeoutError, KeyError, ValueError) as exc:
            row = {
                "item_id": item["id"],
                "split": item["split"],
                "difficulty": item["difficulty"],
                "model": MODEL,
                "correct": 0,
                "error": f"request_error: {exc}",
                "latency_ms": round(
                    (time.perf_counter() - start) * 1000, 2
                ),
                "prompt_tokens": "",
                "output_tokens": "",
                "eval_duration_ns": "",
                "done_reason": "",
                "generated_sql": "",
            }

        rows.append(row)
        print(
            f"{item['id']}: correct={row['correct']}, "
            f"latency={row['latency_ms'] / 1000:.2f}s, "
            f"error={row['error'] or 'none'}"
        )

    save_rows(rows)
    correct = sum(row["correct"] for row in rows)
    print(f"\nSaved {len(rows)} rows to {RESULTS_FILE}")
    print(f"Ollama test accuracy: {correct}/{len(rows)}")


if __name__ == "__main__":
    main()