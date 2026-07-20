"""Generate a daily morning sales report and send it to Telegram."""

import os
import sys
from datetime import datetime
from typing import Any

import requests


def summarize_sales(rows: list[list[Any]]) -> dict[str, Any]:
    """Summarize sales rows into simple daily metrics."""
    if not rows:
        return {
            "sales_count": 0,
            "total_revenue": 0,
            "top_menu": "-",
            "top_menu_qty": 0,
        }

    menu_totals: dict[str, int] = {}
    total_revenue = 0

    for row in rows:
        menu = str(row[1]).strip()
        qty = int(row[2])
        price = float(row[3])
        total = int(row[4]) if len(row) > 4 else int(qty * price)

        menu_totals[menu] = menu_totals.get(menu, 0) + qty
        total_revenue += total

    top_menu, top_menu_qty = max(
        menu_totals.items(), key=lambda item: item[1], default=("-", 0))

    return {
        "sales_count": len(rows),
        "total_revenue": int(total_revenue),
        "top_menu": top_menu,
        "top_menu_qty": int(top_menu_qty),
    }


def build_report_message(summary: dict[str, Any]) -> str:
    """Build the Telegram message body for the morning report."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    return (
        f"📊 รายงานเช้านี้ ({now})\n"
        f"- ยอดขาย: {summary['sales_count']} รายการ\n"
        f"- รายได้รวม: {summary['total_revenue']} บาท\n"
        f"- เมนูขายดี: {summary['top_menu']} ({summary['top_menu_qty']} ชิ้น)"
    )


def fetch_sales_rows() -> list[list[Any]]:
    """Read sales data from Google Sheets if configured."""
    sheet_id = os.environ.get("GOOGLE_SHEETS_ID")
    credentials_json = os.environ.get("GOOGLE_SHEETS_CREDENTIALS")

    if not sheet_id:
        return []

    if not credentials_json:
        return []

    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except Exception as exc:
        raise RuntimeError(
            f"missing dependency for Google Sheets: {exc}") from exc

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    creds = Credentials.from_service_account_info(
        __import__("json").loads(credentials_json),
        scopes=scopes,
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id).worksheet("Sheet1")
    return sheet.get_all_values()


def send_report(message: str) -> None:
    """Send a report via Telegram when bot credentials are configured."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        raise RuntimeError("missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")

    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data={"chat_id": chat_id, "text": message},
        timeout=15,
    )
    response.raise_for_status()


def main() -> int:
    """Main entry-point for the GitHub Action."""
    try:
        rows = fetch_sales_rows()
        summary = summarize_sales(rows[1:] if len(rows) > 1 else [])
        message = build_report_message(summary)
        send_report(message)
        print(message)
        return 0
    except Exception as exc:
        print(f"[ERROR] morning report failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
