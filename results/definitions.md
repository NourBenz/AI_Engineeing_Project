# Project 0 — Definitions

## Task and data

**Natural Language → SQL (NL→SQL):** Turning an English question into a SQL query that answers it using a database.

**SQLite:** The database system used for this project.

**Synthetic data:** Made-up bookstore records created for testing. The generator uses fixed seed `496` so the database can be recreated.

**Item:** One benchmark question stored as one line in `data/items.jsonl`.

**Reference SQL:** The correct SQL answer stored with an item. The model does **not** see it; the scorer uses it afterward as an answer key.

**Dev split:** The 12 practice items used to check the setup and clarify the prompt before the measured run.

**Test split:** The 54 fixed items used to measure each model. All three models must receive the same test items.

## Models

**Local open-weights model:** A model run on our own computer. This project's local model is `qwen2.5-coder:3b` through Ollama.

**Top API model:** A high-capability model accessed through a hosted API. The exact model is pending course access.

**Cheap API model:** A lower-priced model accessed through a hosted API. The exact model and price are pending course access.

**Model tag/version:** The exact model name used for a run. It must be recorded so the result can be identified and repeated.

## Prompt and parameters

**Shared prompt:** The database instructions in `src/prompt.txt` given to every model with each English question.

**Temperature:** A generation setting that controls randomness. The local test used `0`.

**Maximum output tokens:** The longest answer allowed from one call. The local test used `256` tokens, called `num_predict` in Ollama.

**Context window:** The amount of text the model can use as context. Ollama used `num_ctx = 4096`.

**Seed:** A number used to make generation more repeatable. Ollama used `496`. This is separate from the database generator's seed, even though both currently use the same number.

**Sequential calls:** Asking one question, waiting for its complete answer, then asking the next. The local model made 54 sequential test calls.

## Scoring

**Execution-based scoring:** Running the model's SQL and reference SQL on the same database and comparing their returned results.

**Query-result equivalence:** Two SQL queries count as equivalent when their results match under the item's scoring rules. The SQL text itself can be different.

**Order-sensitive item:** An item where result-row order matters, such as a question asking for the top five books in a specific order.

**Correct item:** The model SQL executes and returns a result equivalent to the reference SQL result.

**Incorrect item:** The results differ, or the model SQL is invalid, times out, or fails during execution.

**Accuracy:** Correct test items divided by all test items. The local model's measured result is `31/54 = 57.4%`.

## Timing and tokens

**Latency:** Time from sending one question to receiving the complete model answer. The CSV records it as `latency_ms` (milliseconds).

**p50 latency:** The middle latency after sorting response times; roughly half the calls are faster.

**p95 latency:** A high-end latency; roughly 95% of calls are at or below it. The calculation method should be stated with the result.

**Prompt tokens:** Tokens used to process the input prompt and question.

**Output tokens:** Tokens generated in the answer.

**Output tokens per second:** Generated output tokens divided by generation time. For Ollama, use `output_tokens` and `eval_duration_ns` from `results/per_item.csv`.

**Generation time:** Time spent producing output tokens. It is only part of complete-response latency.

## Cost and files

**API cost:** The provider's charge for input and output tokens, using the exact selected model's prices.

**Cost per 1,000 questions:** An estimate based on the measured average cost per test question multiplied by 1,000. State the prices and calculation used.

**`results/per_item.csv`:** The required detailed results. Each model should have one record for each of the same 54 test items.

**`results/summary.csv`:** The required model-level comparison calculated from per-item results.

**`results/hardware.md`:** The required description of the computer used for the local model and its measured speed.

**`results/local_ollama.md`:** An additional readable explanation of the completed local-model run.