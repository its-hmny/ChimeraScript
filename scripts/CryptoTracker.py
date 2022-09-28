#! /usr/bin/env python3
"""
ChimeraScript - CryptoTracker.py

This script allows, based on a given crypto purchase history, to determine the
current position for each and every purchase. When a purchase has generated a
sufficently high profit the user might chose to sell its position.
The script could be also used to track the positions during the day, week, etc.

Example:
    To get the current exchange rates just one time, use::
        $ python3 CryptoTracker.py {purchase_hist} --recurrent=false

    To get the current exchange rates and refresh them every x seconds, use::
        $ python3 CryptoTracker.py {purchase_hist} --recurrent --refresh_interval={x}


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
from rich.table import Table

# API endpoint to retrieve exchange rates for a given crypto token
COINBASE_EXCHANGE_API = "https://api.coinbase.com/v2/exchange-rates"
# Rich console instance for pretty printing on the terminal
console = Console(record=True)


@dataclass(frozen=True, slots=True)
class Purchase():
    """
    Represents the needed informations about a crypto tokens purchase in order
    to determine the current position (margin or loss) as well as profit/loss
    value and percentage
    """
    amount: float
    crypto_token: str
    fiat_currency: str
    purchase_price: int


def init_table() -> Table:
    """
    Initializes a `rich` table with some specific translated and styled columns
    """
    date_fmt = datetime.now().strftime('%H:%M:%S')
    table = Table(title=f"Current exchange rates at {date_fmt}", style="yellow")

    table.add_column("Crypto amount", justify="right", no_wrap=True)
    table.add_column("Profit margin", justify="right", no_wrap=True)
    table.add_column("Profit percentage", justify="right", no_wrap=True)

    return table


def get_rates_diff(purchase: Purchase) -> Tuple[float, float]:
    """
    Given a `purchase` requests the current exchange rates to CoinBase API
    and computes the current position for given purchase. The current position
    is a tuple of value and percentage (both for profit or loss)

    Args:
        purchase (Purchase): The purchase on which determine the current position
    """
    # Fetches the current exchange rates for the purchased currency
    response = get(COINBASE_EXCHANGE_API, params={"currency": purchase.crypto_token})
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


def main(history_path: PathLike, recurrent: bool = True, refresh_interval: int = 30 * 60) -> None:
    """
    Fetches the current exchange rates from CoinBase ppublic API and prints on the stdout
    a comprehensive report table with the current profit/loss margin based on the purchase
    exchange rates (and costs). When executed in `recurrent` mode, refreshes the quotations 
    every `refresh_interval` seconds

    Args:
        history_path (PathLike): The JSON file path with the purchase history
        recurrent (bool): Flag to execute the script recurrently (just like UNIX cron)
        refresh_interval (int): An optional user defined refresh interval

    Raises:
        FileNotFoundError: Cannot find purchase history JSON file
    """
    # Argument checking and validation
    if not exists(history_path) or not isfile(history_path):
        raise FileNotFoundError(f"{history_path} doesn't exist or isn't a file")

    while True:
        # Reads JSON file with purchase history and converts it to 'Purchase' dataclass list
        json_content = parse_json(open(history_path, "r", encoding="UTF-8"))
        purchases_history = [Purchase(**entry) for entry in json_content]

        table = init_table()  # Initializes a `rich` table to display profit/loss

        for purchase in purchases_history:
            # Determines and format the current profit/loss data in tabular format
            val_diff, perc_diff = get_rates_diff(purchase)
            margin_fmt = f"{val_diff:.2f} {purchase.fiat_currency}"
            perc_fmt = f"{perc_diff:.2f}%"

            table.add_row(
                f"{purchase.amount} {purchase.crypto_token}",
                f"[green]{margin_fmt}[/green]" if val_diff > 0 else f"[red]{margin_fmt}[/red]",
                f"[green]{perc_fmt}[/green]" if val_diff > 0 else f"[red]{perc_fmt}[/red]"
            )

        console.print(table)

        # If we're executing n `recurrent` mode then we pause execution, else we return
        if recurrent and refresh_interval > 0:
            sleep(refresh_interval)
        else:
            return None


if __name__ == "__main__":
    try:
        Fire(main)
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
