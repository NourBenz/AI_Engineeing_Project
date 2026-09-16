# Hardware and local-model performance

Last updated: 2026-09-15

## Computer

- Operating system: Windows
- Computer type: laptop
- RAM: 24 GB DDR4
- Discrete GPU: NVIDIA GeForce RTX 3050 Ti Laptop GPU
- Dedicated discrete-GPU memory: 4 GB
- Integrated GPU also present: Intel Iris Xe Graphics

These details were read from Windows Task Manager. The presence of a GPU does not by itself prove how much of the model Ollama placed on it.

## Local model and runtime

- Model tag: `qwen2.5-coder:3b`
- Runtime: Ollama, running locally
- Database task: Natural Language → SQLite SQL

## Fixed generation settings

- Temperature: 0
- Maximum output: 256 tokens (`num_predict`)
- Context window: 4096 tokens (`num_ctx`)
- Seed: 496
- Streaming: disabled
- Call pattern: 54 test questions, one at a time and sequentially

## Measured results

- Accuracy: **31/54 correct (57.4%)**
- p50 complete-response latency: **3.39 seconds**
- p95 complete-response latency: **4.67 seconds**
- Output generation speed: **65.9 tokens/second**

The latency numbers come from `latency_ms` in `results/per_item.csv`. Output speed was calculated as the sum of generated output tokens divided by the sum of Ollama generation durations across the 54 test calls.

## Measurement limits

- Hardware and electricity costs were not measured.
- Exact GPU offload or GPU utilization during the run was not recorded.