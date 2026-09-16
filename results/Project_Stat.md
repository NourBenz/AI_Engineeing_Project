# Project 0 — Progress Notes

Last updated: 2026-09-15

Natural Language → SQL was approved as the benchmark task. The database, questions, scorer, and local Ollama run are finished. The two API runs and final comparison are waiting for course API access.

## Bookstore database

A small online bookstore was chosen because its tables support simple questions as well as joins, totals, dates, payments, returns, and customers with no orders.

The schema contains `customers`, `categories`, `products`, `orders`, `order_items`, `payments`, and `returns`. It is documented in `data/schema.md` and `data/schema.sql`.

`src/create_db.py` generates the SQLite database with seed `496`, making the data reproducible. The generated data has 120 customers, 8 categories, 80 products, 300 orders, 750 order items, 360 payments, and 60 returns.

The data includes edge cases: 12 customers have no orders, 12 products were never ordered, 45 orders were cancelled, and payments include both successes and failures. `src/check_db.py` found no foreign-key errors.

**Current state:** finished.

## Questions

`data/items.jsonl` contains 12 dev questions and 54 test questions. The test set has 18 easy, 20 medium, and 16 hard items. The 54 test items exceed the P0 minimum of 50.

Each item has an English question and a reference SQL query. The English question goes to the model. The reference SQL stays in the scoring code as the answer key.

The dev questions were used to check the setup and clarify the prompt. The test questions were used for the measured result. Keeping those separate prevents prompt changes based on the questions used to report accuracy.

The reference queries were executed with `src/check_db.py`. A final wording check is still useful because valid SQL does not automatically prove that every English question is perfectly clear.

**Current state:** written and executable. The test set is fixed for the remaining model runs.

## Prompt and scoring

`src/prompt.txt` gives the model the bookstore tables, relationships, business definitions, and one English question. The same prompt is intended for all three models.

The local dev run exposed two misunderstandings: unrequested active-customer filters and treating a return record as if every purchased unit had been returned. The prompt was clarified before the test run.

`src/score.py` checks an answer by running both the model SQL and the reference SQL on the bookstore database. Matching query results count as correct even when the SQL text differs. Invalid SQL and wrong results count as incorrect.

**Current state:** prompt and scorer are fixed for the model comparison.

## Local model

`qwen2.5-coder:3b` was selected for the local run. It is a code-focused Ollama model of a practical size for the laptop's 4 GB dedicated GPU memory.

The run used temperature `0`, a 256-token answer limit, a 4096-token Ollama context window, and seed `496`. Questions were sent one at a time.

The dev run finished at **10/12 correct** after the prompt clarification. The measured test run made 54 sequential calls and finished at **31/54 correct (57.4%)**. All 54 answers, scores, errors, timings, and token counts are saved in `results/per_item.csv`.

The calculated p50 response time is **3.39 seconds**. The p95 response time is **4.67 seconds**. Output generation speed is **65.9 tokens per second**. Details are recorded in `results/local_ollama.md` and `results/hardware.md`.

These numbers describe the local model only. GPU offload during the run was not measured.

**Current state:** finished.

## API models

P0 also requires a top API model and a cheaper API model. The exact models have not been selected because course API access has not been provided yet.

Both models need the same fixed prompt, the same 54 test questions in the same order, temperature `0`, and the same 256-token answer limit where supported. Each response needs to be scored and saved with its latency and token usage.

**Current state:** waiting for API access. No API results exist yet.

## Final comparison and documents

Once all three model runs are complete, `results/summary.csv` needs to be calculated from the per-item records. It will show accuracy, p50/p95 latency, and cost for each model. The API cost calculation must use actual token usage and the prices of the exact models selected.

The README, two-page report, and one-page postmortem still need their final content. Reported numbers should match the saved CSV results.

**Current state:** pending the API runs.

## Running notes

- Database generated with fixed seed `496`; planned edge cases and foreign keys checked.
- 12 dev and 54 test items written; reference SQL executed.
- Local Ollama model downloaded and connected to `src/run.py`.
- Prompt clarified using dev questions before the test run.
- Ollama test run completed: 31/54 correct across 54 sequential calls.
- Local measurements calculated: p50 3.39 seconds, p95 4.67 seconds, output speed 65.9 tokens per second.

Add a dated note here after each new run or document update. Keep pending results blank until measured.