# BugFlow Load Test

BugFlow Load Test is a lightweight, Python-based tool for authorized load and performance testing of web applications and APIs.

It helps you generate controlled traffic, measure response behavior, and collect simple performance metrics in environments where you have explicit permission to test.

## Features

- Controlled HTTP load generation.
- Configurable concurrency, duration, and request rate.
- Async-based architecture for efficient execution.
- Basic latency and error statistics.
- CSV, TXT, and Markdown reports.
- Easy to extend for custom test scenarios.

## Use Cases

- Performance benchmarking.
- Capacity validation.
- Regression testing before release.
- Monitoring and alert verification.
- Authorized resilience testing.

## Requirements

- Python 3.10 or newer.
- `aiohttp`.
- A target system you are authorized to test.

## Installation

```bash
git clone https://github.com/<your-username>/bugflow-load-test.git
cd bugflow-load-test
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python3 bugflow_load.py --target https://example.com --users 20 --duration 60 --rps 5 --out results
```

## Parameters

- `--target`: Target URL to test.
- `--users`: Number of concurrent workers.
- `--duration`: Test duration in seconds.
- `--rps`: Request rate limit.
- `--timeout`: Request timeout in seconds.
- `--out`: Output directory.

## Output Files

The tool writes the following files to the output directory:

- `report.md` — Markdown summary of the test.
- `report.txt` — Plain-text summary.
- `results.csv` — CSV version of the results.

## Safety Notice

Use this tool only on systems you own or are explicitly authorized to test.

Do not use it against third-party systems without permission.

## License

MIT
