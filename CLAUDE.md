# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**iscrapyd-project** is a Scrapy-based data collection system for financial market data (crypto and stocks), deployed via scrapyd daemon with optional Telegram alerting.

## Setup

The project root is itself a Python 3.9.6 virtual environment:

```bash
source bin/activate
pip install -r requirements.txt
```

Required environment variables (see `.env.example`):
- `CMC_API_KEY` — CoinMarketCap Pro API key (required for coin-market spider)
- `DB_PATH` — Path for SQLite databases
- `TELE_TOKEN` — Telegram bot token
- `TELE_ALARM_ID` — Telegram chat ID for alerts

## Running Spiders

All `scrapy` commands must be run from the `iscrapy/` directory (where `scrapy.cfg` lives):

```bash
cd iscrapy
scrapy crawl coin-market
scrapy crawl yahoo-finance -a symbol=BTC-USD
scrapy crawl sina-finance -a symbol=sz399006
```

To run the scrapyd daemon and deploy spiders:

```bash
scrapyd                  # starts daemon on localhost:6800
scrapyd-deploy           # deploys current project to local daemon
```

## Architecture

### Data Flow

```
Spider → ConditionalPipeline (100) → StorePipeline (150) → TelegramPipeline (300, disabled)
```

All data passes through `IscrapyItem` with four fields: `item_id` (dedup key), `data` (payload dict), `failed` (bool), `msg` (Telegram-formatted string).

### Pipelines (`iscrapy/iscrapy/pipelines.py`)

- **ConditionalPipeline** — Deduplicates `coin-market` items via SQLite; drops items where price change < 1% from the previous run.
- **StorePipeline** — Persists OHLCV data to `<DB_PATH>/<symbol>.db` using upsert on the `ohlc` table (keyed on timestamp).
- **TelegramPipeline** — Sends `msg` field to Telegram; disabled by default in `settings.py`.

### Spiders (`iscrapy/iscrapy/spiders/`)

| Spider | Source | Key argument |
|--------|--------|--------------|
| `coin_market.py` | CoinMarketCap Pro API v2 | none (uses `CRYPTO_IDS` setting) |
| `yahoo_finance.py` | Yahoo Finance chart API | `symbol` (default: `BTC-USD`) |
| `sina_finance.py` | Sina Finance proprietary API | `symbol` (default: `sz399006`) |

`CRYPTO_IDS` in `settings.py` controls which coin IDs are fetched (currently `["1", "1027"]` = BTC, ETH).

### Key Settings (`iscrapy/iscrapy/settings.py`)

- `CRYPTO_IDS` — List of CoinMarketCap coin IDs to track
- `DB_PATH` — Base path for SQLite `.db` files
- `ITEM_PIPELINES` — Pipeline priority map; set value to `None` to disable a pipeline

## No Tests

There are no automated tests. Validate changes by running the spider directly and inspecting logs/database output.
