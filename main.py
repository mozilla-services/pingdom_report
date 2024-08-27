import argparse
import datetime
import os

from dotenv import load_dotenv
import requests
import pandas as pd
from premailer import transform


load_dotenv()


PINGDOM_API_TOKEN = os.getenv("PINGDOM_API_TOKEN")

PINGDOM_API_URL = "https://api.pingdom.com/api/3.1"

PARENT_DIR = "reports/"

HEADERS = {"Authorization": f"Bearer {PINGDOM_API_TOKEN}", "Accept-Encoding": "gzip"}


def get_checks(tags):
    payload = {"tags": tags}
    r = requests.get(f"{PINGDOM_API_URL}/checks", headers=HEADERS, params=payload)
    r.raise_for_status()

    if not r.json()["checks"]:
        print(f"No checks found using tags: {tags}")
        exit()

    return [
        [check["id"], check["name"], check["hostname"], check["status"]]
        for check in r.json()["checks"]
    ]


def downtime_outages(check_id, from_date, to_date):
    """Calculate the number of downtimes and downtime seconds given a pingdom check_id and date range

    Args:
        check_id (integer): pingdom check_id
        from_date (float): UNIX timestamp, beginning of time period
        to_date (float): UNIX timestamp, end of time period

    Returns:
        tuple: downtime (integer, minutes), outages (integer, count)
    """
    payload = {"from": from_date, "to": to_date}
    r = requests.get(
        f"{PINGDOM_API_URL}/summary.outage/{check_id}", headers=HEADERS, params=payload
    )

    outages = 0
    downtime = 0
    for state in r.json()["summary"]["states"]:
        if state["status"] == "down":
            outages += 1
            downtime += state["timeto"] - state["timefrom"]

    return downtime, outages


def average_uptime(check_id, from_date, to_date):
    """Get response_time, and calculate uptime given a pingdom check_id and date range

    Args:
        check_id (integer): pingdom check_id
        from_date (float): UNIX timestamp, beginning of time period
        to_date (float): UNIX timestamp, end of time period

    Returns:
        tuple: response_time (integer, ms), uptime_percent (integer, percent)
    """
    payload = {"from": from_date, "to": to_date, "includeuptime": "true"}
    r = requests.get(
        f"{PINGDOM_API_URL}/summary.average/{check_id}", headers=HEADERS, params=payload
    )

    response_time = r.json()["summary"]["responsetime"]["avgresponse"]

    status = r.json()["summary"]["status"]
    uptime_percent = 100 - (status["totaldown"] / sum(status.values()) * 100)

    return response_time, uptime_percent


def get_time_hh_mm_ss(seconds):
    mm, ss = divmod(seconds, 60)
    hh, mm = divmod(mm, 60)

    return f"{hh}h {mm}m {ss}s"


def generate_html_report(
    checks, from_date, to_date, days, report_name, file_name, tags
):
    df_checks = pd.DataFrame(checks)
    df_checks.columns = [
        "CHECK_ID",
        "CHECK_NAME",
        "CHECK NAME",
        "HOSTNAME",
        "STATUS",
        "DOWNTIME_MINUTES",
        "DOWNTIME",
        "OUTAGES",
        "RESPONSE TIME",
        "UPTIME",
    ]

    # Create overview data from checks data
    overview_count = len(checks)
    overview_uptime = df_checks["UPTIME"].mean()
    overview_outages = df_checks["OUTAGES"].sum()
    overview_response_times = df_checks["RESPONSE TIME"].mean()
    overview_downtime = get_time_hh_mm_ss(df_checks["DOWNTIME_MINUTES"].sum())
    df_overview = pd.DataFrame(
        columns=["UPTIME", "OUTAGES", "DOWNTIME", "RESPONSE TIME", "NUMBER OF CHECKS"],
        data=[
            [
                overview_uptime,
                overview_outages,
                overview_downtime,
                overview_response_times,
                overview_count,
            ]
        ],
    )

    # create dataframes for checks w/o downtime and add unit labels
    df_checks_y_downtime = df_checks[df_checks.OUTAGES != 0].sort_values(
        by="OUTAGES", ascending=False
    )
    df_checks_n_downtime = df_checks[df_checks.OUTAGES == 0].sort_values(
        by="CHECK_NAME"
    )

    header_text = f"{days} Uptime Report"
    page_title_text = header_text
    header_date = f'{from_date.strftime("%Y-%m-%d")} to {to_date.strftime("%Y-%m-%d")}'
    overview_text = f"OVERVIEW: {report_name} - {days}"
    checks_y_downtime_text = "CHECKS WITH DOWNTIME"
    checks_y_downtime_hidden_columns = [
        "CHECK_ID",
        "CHECK_NAME",
        "STATUS",
        "DOWNTIME_MINUTES",
    ]
    checks_n_downtime_text = "CHECKS WITHOUT DOWNTIME"
    check_n_downtime_hidden_columns = [
        "CHECK_ID",
        "CHECK_NAME",
        "STATUS",
        "DOWNTIME",
        "DOWNTIME_MINUTES",
        "OUTAGES",
    ]

    pd.set_option("colheader_justify", "left")
    html = f"""
    <html>
      <head>
        <title>{page_title_text}</title>
        <style>
          table {{width:100%;border-collapse:collapse;margin-left:auto;margin-right:auto}}
          th {{color:#fff;background-color:#222;border:1px solid #000;padding:5px 10px;font-size:12px;font-family:Arial,sans-serif;text-align:left}}
          td {{color:#000;background-color:#fff;border:1px solid #ddd;padding:10px 10px;font-size:13px;font-family:Arial,sans-serif}}
          h2 {{margin-bottom:10px;font-family:Arial,sans-serif;font-size:16px}}
          h3 {{margin-bottom:10px;font-family:Arial,sans-serif;font-size:13px}}
        </style>
      </head>
      <body>
        <table style=width:100%;margin-left:auto;margin-right:auto;border:0px>
          <tr>
            <td>
              <table style="width:100%;height:100%;margin:0px;padding:0px;border:0px;background:#222;border-collapse:collapse" cellspacing="0" cellpadding="0" border="0">
                <tbody>
                  <tr>
                    <td style="border:0px;background:#000;padding-left:30px;padding-right:5px;padding-top:20px;padding-bottom:20px">
                      <img style="display:block" src="https://mozilla.design/files/2019/06/mozilla-logo-bw-rgb.png" width="150" border="0">
                    </td>
                    <td style="border:0px;background-color:#000;padding-top:20px;padding-bottom:20px" width="60%"></td>
                    <td style="border:0px;background:#000;color:white;font-size:12px;font-family:Arial,sans-serif;padding-top:20px;padding-bottom:20px">
                      <td style="border:0px;background:#000;color:white;font-size:14px;font-family:Arial,sans-serif;text-align:right;padding-right:30px">
                        <span style="margin-bottom:3px;color:#fff333;font-size:14px">{header_text}</span>
                        <br>
                        {header_date}
                      </td>
                    </td>
                  </tr>
                </tbody>
              </table>
            </td>
          <tr>
            <td style="background:#f7f7f7;border-left:0px solid #ddd;border-right:0px solid #ddd;border-bottom:0px solid #ddd;padding:30px">
              <h2>{overview_text}</h2>
              {df_overview .style
              .format({'UPTIME': "{:.3f}%", "RESPONSE TIME": "{:.0f} ms"})
              .hide()
              .to_html()}
            </td>
          </tr>
          <tr>
            <td style="background:#f7f7f7;border-left:0px solid #ddd;border-right:0px solid #ddd;border-bottom:0px solid #ddd;padding:30px">
              <h3>{checks_y_downtime_text}</h2>
              {df_checks_y_downtime.style
              .format({'UPTIME': "{:.3f}%", "RESPONSE TIME": "{:.0f} ms"})
              .bar(color="#00ff00", subset=["RESPONSE TIME"], align="mid")
              .bar(color="#ff4500", subset=["OUTAGES"], align="mid")
              .hide()
              .hide(checks_y_downtime_hidden_columns, axis='columns')
              .to_html()}
            </td>
          </tr>
          <tr>
            <td style="background:#f7f7f7;border-left:0px solid #ddd;border-right:0px solid #ddd;border-bottom:0px solid #ddd;padding:30px">
              <h3>{checks_n_downtime_text}</h2>
              {df_checks_n_downtime.style
              .format({"UPTIME": "{:.0f}%","RESPONSE TIME": "{:.0f} ms"})
              .bar(color="#00ff00", subset=["RESPONSE TIME"], align="mid")
              .hide(check_n_downtime_hidden_columns, axis="columns")
              .hide()
              .to_html()}
            </td>
          </tr>
          <tr>
            <td style="background:#f7f7f7;border-left:0px solid #ddd;border-right:0px solid #ddd;border-bottom:0px solid #ddd;padding:3px">
              <span style="float:left;font-size:8pt">Made with 💚 by sre: green; maintained by obs-team</span>
              <span style="float:right;font-size:8pt">tags used to generate this report: {tags}</span>
            </td>
          </tr>
        </table>
    </html>
      </body>
    """

    try:
        os.mkdir(PARENT_DIR)
    except FileExistsError:
        pass

    fixed_html = transform(html, pretty_print=True)
    with open(f"{PARENT_DIR}/{file_name}", "w") as f:
        f.write(fixed_html)


def main(days, tags, report_name):
    try:
        from_date = datetime.datetime.now() - datetime.timedelta(days)
        to_date = datetime.datetime.now()
        days = f"{days} day"
        file_name = f"{days}_pingdom_report.html"
    except TypeError:
        # produce monthly report
        # last day of previous month
        to_date = datetime.datetime.combine(
            datetime.date.today().replace(day=1) - datetime.timedelta(days=1),
            datetime.time(23, 59, 59),
        )

        # first day for previous month
        from_date = datetime.datetime.combine(
            datetime.date.today().replace(day=1) - datetime.timedelta(days=to_date.day),
            datetime.time(0, 0, 0),
        )
        days = to_date.strftime("%B, %Y")
        file_name = f'{to_date.strftime("%B")}_pingdom_report.html'
    finally:
        unix_from_date = from_date.timestamp()
        unix_to_date = to_date.timestamp()

    # collect check data for checks with specific tags
    checks = get_checks(tags)
    for check in checks:
        link_text = f'<a href="https://my.pingdom.com/app/reports/uptime#check={check[0]}&daterange={days}days">{check[1]}</a>'
        check.insert(2, link_text)
        downtime_minutes, outages = downtime_outages(
            check[0], unix_from_date, unix_to_date
        )
        response_time, uptime_percent = average_uptime(
            check[0], unix_from_date, unix_to_date
        )
        downtime_formatted = get_time_hh_mm_ss(downtime_minutes)
        check.extend(
            (
                downtime_minutes,
                downtime_formatted,
                outages,
                response_time,
                uptime_percent,
            )
        )
        #             0      1        2         3        4            5          6             7              8              9
        # checks [check_id, name, link_text, hostname, status, downtime_minutes, downtime, total_outages, response_time, uptime_percent]

    generate_html_report(checks, from_date, to_date, days, report_name, file_name, tags)
    # TODO: handle missing checks?
    # TODO: print list of available tags


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="pingdom_report",
        description="Create a custom pingdom report for the previous month from tagged checks",
    )
    parser.add_argument(
        "-d",
        "--days",
        metavar="DAYS",
        action="store",
        type=int,
        help="Specify previous n days to cover instead of previous month",
    )
    parser.add_argument(
        "-t",
        "--tags",
        metavar="TAGS",
        action="store",
        default="bug_bounty_site",
        help="comma separated list of tags",
    )
    parser.add_argument(
        "-r",
        "--report-name",
        metavar="REPORT_NAME",
        action="store",
        default="Critical Sites Monthly Uptime",
    )
    args = parser.parse_args()

    main(args.days, args.tags, args.report_name)
