# Local model results — Ollama

Last updated: 2026-09-15  
Status: Local test run and measurements complete

## Model

- Exact model: `qwen2.5-coder:3b`
- Runtime: Ollama on a Windows laptop
- Role in P0: Locally run open-weights model
- Why chosen: A code-focused model of a practical size for this laptop's 4 GB dedicated GPU memory

## Run settings

- Shared prompt: `src/prompt.txt`
- Temperature: `0`
- Maximum output: `256` tokens (`num_predict`)
- Context window: `4096` tokens (`num_ctx`)
- Seed: `496`
- Streaming: disabled
- Test calls: one question per call, sequentially

## Accuracy

- Dev run: **10/12 correct** after clarifying the prompt
- Test run: **31/54 correct (57.4%)**

The dev items were used to check the setup before testing. The 54 test items measured the local model's performance. The model did not receive the reference SQL answers.

## Latency and generation speed

- p50 complete-response latency: **3.39 seconds**
- p95 complete-response latency: **4.67 seconds**
- Output generation speed: **65.9 tokens/second**

Complete-response latency measures the time from sending a question to receiving the full answer. Output speed uses Ollama's generated-token counts divided by its generation durations. The p95 value uses the nearest-rank method.

## How answers were scored

`src/score.py` ran the model's SQL and the item's reference SQL on the same bookstore database. An answer was correct when the query results were equivalent. Incorrect results and SQL execution errors counted as wrong answers.

All 54 per-question SQL answers, scores, errors, latencies, and token measurements are in `results/per_item.csv`.

## Hardware and cost

- RAM: 24 GB DDR4
- GPU: NVIDIA GeForce RTX 3050 Ti Laptop GPU
- Dedicated GPU memory: 4 GB
- Full hardware record: `results/hardware.md`
- Hosted API charge for this local run: none
- Hardware and electricity costs: not measured

## Remaining comparison work

The top API model and cheap API model have not been run because course API access has not yet been provided. Their results will be compared with this fixed 54-item local run.