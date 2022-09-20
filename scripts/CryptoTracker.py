#! /usr/bin/env python3
"""
ChimeraScript - CryptoTracker.py

This script allows to ... TODO: Add documentation

Example: TODO: add example usages
    To only pull from Google Drive, use::
        $ python3 DriveDiffMerger.py sync ~/GoogleDrive


Copyright 2022 Enea Guidi (hmny). All rights reserved.
This file are distributed under the General Public License v 3.0.
A copy of abovesaid license can be found in the LICENSE file.
"""
from dataclasses import dataclass
from datetime import datetime
from json import load as parse_json
from os import PathLike
from os.path import basename, exists, isfile
from time import sleep
from typing import Tuple

from fire import Fire
from requests import get
from rich.console import Console

# API endpoint to retrieve exchange rates for a given crypto token
COINBAE_EXCHANGE_API = "https://api.coinbase.com/v2/exchange-rates"
REPORT_MSG = \
    "Current profit for '{0} {1}' is {2:.2f} ({3:.2f}%)"
# Rich console instance for pretty printing on the terminal
console = Console(record=True)


@dataclass(frozen=True, slots=True)
class Purchase():
    """TODO: add pydoc annotatios"""
    amount: float
    crypto_token: str
    fiat_currency: str
    purchase_price: int


def get_rates_diff(purchase: Purchase) -> Tuple[float, float]:
    """TODO: Add pydoc annotations"""
    # Fetches the current exchange rates for the purchased currency
    response = get(COINBAE_EXCHANGE_API, params={"currency": purchase.crypto_token})
    # Bails out if API returns any kind of error error
    if not response.ok:
        console.print(f"[red]Couldn't find rates for token '{purchase.crypto_token}'[/red]")

    # Parses the response and extracts the exchange rates for the provided FIAT currency
    currency_exchange_rates = response.json()["data"]["rates"]
    current_exhange = float(currency_exchange_rates[purchase.fiat_currency])
    # Computes the current quotation and the one at purchase time
    quotation_now = current_exhange * purchase.amount
    quotation_purchase = purchase.purchase_price * purchase.amount

    # Determines some data/analytics based on current and historical data
    diff_value = quotation_now - quotation_purchase
    diff_percentage = (quotation_now * 100 / quotation_purchase) - 100
    return (diff_value, diff_percentage)


def live_refresh(config_file: PathLike, timeout_interval: int = 30 * 60) -> None:
    """TODO: Add pydoc annotations"""
    while True:
        hour_fmt = datetime.now().strftime("%H:%M:%S")
        console.print(f"[yellow]:hourglass: {hour_fmt} Refreshing exhanges rates and diffs[yellow]")
        # Refreshes the exhange rates diff and waits for the user-defined timeout
        calc_diff(config_file), sleep(timeout_interval)


def calc_diff(config_file: PathLike) -> None:
    """TODO: Add pydoc annotations"""
    # Argument checking and validation
    if not exists(config_file) or not isfile(config_file):
        raise FileNotFoundError(f"{config_file} doesn't exist or isn't a file")

    # Reads JSON file with purchase history and converts it to 'Purchase' dataclass
    json_content = parse_json(open(config_file, "r", encoding="UTF-8"))
    purchase_history = [Purchase(**entry) for entry in json_content]

    for purchase in purchase_history:
        value_diff, percentage_diff = get_rates_diff(purchase)
        # Formats a report template msg with data and print with red or green color based on status
        msg = REPORT_MSG.format(purchase.amount, purchase.crypto_token, value_diff, percentage_diff)
        console.print(f"[green]{msg}[/green]" if value_diff > 0 else f"[red]{msg}[/red]")


if __name__ == "__main__":
    try:
        Fire({"diff": calc_diff, "live": live_refresh})
    except KeyboardInterrupt:
        console.print("[yellow]Interrupt received, closing now...[/yellow]")
    except Exception:
        console.print("[red]An unexpected error occurred[/red]")
        console.print_exception()
    finally:
        script_name = basename(__file__)
        current_date = datetime.now().strftime('%d-%m-%Y %H:%M')
        console.save_html(f"logs/{script_name} {current_date}.html", clear=False)
        console.save_text(f"logs/{script_name} {current_date}.log", clear=False)
