# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a [Scrapy](https://scrapy.org/) + [scrapyd](https://scrapyd.readthedocs.io/) project that scrapes financial data and delivers alerts via Telegram. The project root is a Python virtualenv; the Scrapy project lives in `iscrapy/`.

## Environment Setup

Copy `.env.example` and populate the variables before running:

```
CMC_API_KEY=    # CoinMarketCap Pro API key
DB_PATH=        # Directory path where SQLite DBs are written
TELE_TOKEN=     # Telegram bot token
TELE_ALARM_ID=  # Telegram channel/chat ID for error alerts
```

## Running Spiders

All Scrapy commands must be run from inside `iscrapy/` (where `scrapy.cfg` lives):

```bash
cd iscrapy

# Run CoinMarketCap spider
scrapy crawl coin-market

# Run Yahoo Finance spider (symbol passed as spider arg)
scrapy crawl yahoo-finance -a symbol=BTC-USD
scrapy crawl yahoo-finance -a symbol=GC=F   # gold

# Deploy to local scrapyd (must be running on port 6800)
scrapyd-deploy
```

## Architecture

### Data flow

Spider → `ConditionalPipeline` (priority 100) → `StorePipeline` (priority 150) → optional `TelegramPipeline` (disabled by default, priority 300)

### Spiders (`iscrapy/iscrapy/spiders/`)

- **`coin_market.py`** — hits CoinMarketCap Pro API v2 for cryptocurrency quotes. Crypto IDs to fetch are configured via `CRYPTO_IDS` in settings (default: Bitcoin `"1"` and Ethereum `"1027"`).
- **`yahoo_finance.py`** — hits Yahoo Finance chart API for daily OHLCV data. `symbol`, `period1`, and `period2` can be passed as spider arguments; defaults to last 5 days of `BTC-USD`.

### Items (`iscrapy/iscrapy/items.py`)

All spiders yield `IscrapyItem` with four fields:
- `item_id` — unique identifier (symbol string or timestamp int)
- `data` — dict with the scraped payload
- `failed` — bool; on parse error, `failed=True` and `msg` contains the error
- `msg` — formatted string for Telegram

### Pipelines (`iscrapy/iscrapy/pipelines.py`)

- **`ConditionalPipeline`** — deduplicates `coin-market` items using a local SQLite DB (`./coin-market.db`). Drops an item if the price hasn't moved more than 1% since the last run.
- **`StorePipeline`** — persists `yahoo-finance` OHLCV rows to `<DB_PATH>/<symbol>.db` using an `ohlc` table with `timestamp` as primary key (upsert semantics).
- **`TelegramPipeline`** — sends formatted messages to the configured Telegram channel. Disabled by default; enable in `ITEM_PIPELINES` in `settings.py`.

### scrapyd

The local scrapyd daemon (`http://localhost:6800`) hosts deployed spiders. The `iscrapy/dbs/` directory contains scrapyd's internal databases.
