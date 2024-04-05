# Pingdom Report generator

Creates a html report on pingdom sites.

## Description

Configurable report, using tags to select sites, with a configurable date range.

## Getting Started

### Dependencies

* pyenv (reommended)
* pip install -r requirements.txt

### Installing

* git clone https://github.com/mozilla-it/pingdom_report 
* Add your pingdom API token to `.env`:
```
PINGDOM_API_TOKEN="YOUR_TOKEN_HERE"
```

### Executing program

* Generate a report for the past month, using default tags
```
python main.py
```
* Generate a report for the last 35 days, for sites tagged with `bug_bounty_site`
```
python main.py -d 35 -t bug_bounty_site
```
