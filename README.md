# Pingdom Report generator

Creates a html report on pingdom sites.

## Description

Configurable report, using tags to select sites, with a configurable date range.

## Getting Started

### Requisites

* [uv](https://docs.astral.sh/uv/)

### Token

Add your pingdom API token to `.env`:

```
PINGDOM_API_TOKEN="YOUR_TOKEN_HERE"
```

### Executing program

Reports are added to a `reports/` directory, which is ignored by git.

Generate a report for the past month, using default tags:

```
uv run build_report.py
```

Generate a report for the last 35 days, for sites tagged with `bug_bounty_site`:

```
uv run build_report.py -d 35 -t bug_bounty_site
```
