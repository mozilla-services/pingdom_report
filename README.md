# Pingdom Report generator

Creates a html report on pingdom sites.

## Description

Configurable report, using tags to select sites, with a configurable date range.

## Getting Started

### Building environment

Clone repository and build a virtual environment:

```
git clone https://github.com/mozilla-it/pingdom_report
make build
```

Add your pingdom API token to `.env`:

```
PINGDOM_API_TOKEN="YOUR_TOKEN_HERE"
```

### Executing program

Reports are added to a `reports/` directory, which is ignored by git.

Generate a report for the past month, using default tags:

```
./run.sh
```

Generate a report for the last 35 days, for sites tagged with `bug_bounty_site`:

```
./run.sh -d 35 -t bug_bounty_site
```
