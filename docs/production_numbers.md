## Production numbers (measured 21 Nov 2026 on http://127.0.0.1:8000)

| Metric | Value |
|---|---|
| Questions tested | 10 |
| Cold latency p50 / p95 | 7 ms / 318 ms |
| Cached latency p50 / p95 | 6 ms / 10 ms |
| Cache speed-up (avg) | 6.2x |
| Cache hit rate (server) | 0% |
| Avg tokens / LLM request (prompt + completion) | 0 + 0 |
| Token source | n/a |
| Over-long input (600 chars) | HTTP 200 (expected 413) |
| Prompt-injection attempt | HTTP 200, blocked=None |
