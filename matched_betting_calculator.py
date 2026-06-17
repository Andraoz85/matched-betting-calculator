"""
Matched Betting Calculator for Swedish users (SEK).

How to run:
    pip install streamlit
    streamlit run matched_betting_calculator.py
"""

from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import streamlit as st


THE_ODDS_API_BASE_URL = "https://api.the-odds-api.com/v4"

BOOKMAKERS_BY_REGION: Dict[str, Dict[str, str]] = {
    "United States": {
        "betonlineag": "BetOnline.ag",
        "betmgm": "BetMGM",
        "betrivers": "BetRivers",
        "betus": "BetUS",
        "bovada": "Bovada",
        "williamhill_us": "Caesars",
        "draftkings": "DraftKings",
        "fanatics": "Fanatics",
        "fanduel": "FanDuel",
        "lowvig": "LowVig.ag",
        "mybookieag": "MyBookie.ag",
    },
    "United States 2": {
        "ballybet": "Bally Bet",
        "betanysports": "BetAnySports",
        "betparx": "betPARX",
        "espnbet": "ESPN BET",
        "fliff": "Fliff",
        "hardrockbet": "Hard Rock Bet",
        "hardrockbet_az": "Hard Rock Bet AZ",
        "hardrockbet_fl": "Hard Rock Bet FL",
        "hardrockbet_oh": "Hard Rock Bet OH",
        "rebet": "ReBet",
    },
    "United States Exchanges": {
        "betopenly": "BetOpenly",
        "kalshi": "Kalshi",
        "novig": "Novig",
        "polymarket": "Polymarket",
        "prophetx": "ProphetX",
    },
    "Australia": {
        "betfair_ex_au": "Betfair Exchange AU",
        "betr_au": "Betr AU",
        "betright": "Bet Right",
        "bet365_au": "Bet365 AU",
        "dabble_au": "Dabble AU",
        "ladbrokes_au": "Ladbrokes AU",
        "neds": "Neds",
        "playup": "PlayUp",
        "pointsbetau": "PointsBet AU",
        "sportsbet": "SportsBet",
        "tab": "TAB",
        "tabtouch": "TABtouch",
        "unibet": "Unibet AU",
    },
    "France": {
        "betclic_fr": "Betclic FR",
        "netbet_fr": "NetBet FR",
        "pmu_fr": "PMU FR",
        "unibet_fr": "Unibet FR",
        "winamax_fr": "Winamax FR",
    },
    "Sweden": {
        "atg_se": "ATG",
        "betinia_se": "Betinia",
        "betmgm_se": "BetMGM SE",
        "betsson": "Betsson",
        "campobet_se": "CampoBet",
        "expekt_se": "Nya Expekt",
        "hajper_se": "Hajper",
        "leovegas_se": "LeoVegas SE",
        "mrgreen_se": "Mr Green",
        "nordicbet": "NordicBet",
        "sport888_se": "888sport SE",
        "svenskaspel_se": "Svenska Spel",
        "unibet_se": "Unibet SE",
    },
    "Europe": {
        "onexbet": "1xBet",
        "sport888": "888sport",
        "betclic_fr": "Betclic FR",
        "betanysports": "BetAnySports",
        "betfair_ex_eu": "Betfair Exchange EU",
        "betonlineag": "BetOnline.ag",
        "betsson": "Betsson",
        "codere_it": "Codere IT",
        "betvictor": "BetVictor",
        "coolbet": "Coolbet",
        "everygame": "Everygame",
        "gtbets": "GTbets",
        "leovegas_se": "LeoVegas SE",
        "marathonbet": "Marathon Bet",
        "matchbook": "Matchbook",
        "mybookieag": "MyBookie.ag",
        "nordicbet": "NordicBet",
        "pinnacle": "Pinnacle",
        "pmu_fr": "PMU FR",
        "suprabets": "Suprabets",
        "tipico_de": "Tipico DE",
        "unibet_fr": "Unibet FR",
        "unibet_it": "Unibet IT",
        "unibet_nl": "Unibet NL",
        "unibet_se": "Unibet SE",
        "williamhill": "William Hill",
        "winamax_de": "Winamax DE",
        "winamax_fr": "Winamax FR",
    },
    "United Kingdom": {
        "sport888": "888sport",
        "betfair_ex_uk": "Betfair Exchange UK",
        "betfair_sb_uk": "Betfair Sportsbook UK",
        "betfred_uk": "Betfred UK",
        "betvictor": "BetVictor",
        "betway": "Betway",
        "boylesports": "BoyleSports",
        "casumo": "Casumo",
        "coral": "Coral",
        "grosvenor": "Grosvenor",
        "ladbrokes_uk": "Ladbrokes UK",
        "leovegas": "LeoVegas",
        "livescorebet": "LiveScore Bet",
        "matchbook": "Matchbook",
        "paddypower": "Paddy Power",
        "skybet": "Sky Bet",
        "smarkets": "Smarkets",
        "unibet_uk": "Unibet UK",
        "virginbet": "Virgin Bet",
        "williamhill": "William Hill UK",
    },
}

REGION_KEYS = {
    "United States": "us",
    "United States 2": "us2",
    "United States Exchanges": "us_ex",
    "Australia": "au",
    "France": "fr",
    "Sweden": "se",
    "Europe": "eu",
    "United Kingdom": "uk",
}

SWEDISH_LICENSED_BOOKMAKERS = BOOKMAKERS_BY_REGION["Sweden"]

DEMO_SPORTS = [
    {
        "key": "soccer_demo",
        "group": "Football",
        "title": "Demo Matches",
        "active": True,
    }
]

DEMO_ODDS_EVENTS: List[Dict[str, Any]] = [
    {
        "home_team": "Ghana",
        "away_team": "Panama",
        "commence_time": "2026-06-18T01:00:00Z",
        "bookmakers": [
            {
                "key": "unibet_se",
                "title": "Unibet SE",
                "last_update": "2026-06-16T12:00:00Z",
                "markets": [
                    {
                        "key": "h2h",
                        "outcomes": [
                            {"name": "Ghana", "price": 2.28},
                            {"name": "Draw", "price": 3.50},
                            {"name": "Panama", "price": 3.20},
                        ],
                    }
                ],
            },
            {
                "key": "betsson",
                "title": "Betsson",
                "last_update": "2026-06-16T12:01:00Z",
                "markets": [
                    {
                        "key": "h2h",
                        "outcomes": [
                            {"name": "Ghana", "price": 2.24},
                            {"name": "Draw", "price": 3.45},
                            {"name": "Panama", "price": 3.25},
                        ],
                    }
                ],
            },
            {
                "key": "smarkets",
                "title": "Smarkets",
                "last_update": "2026-06-16T12:02:00Z",
                "markets": [
                    {
                        "key": "h2h_lay",
                        "outcomes": [
                            {"name": "Ghana", "price": 2.34, "available": 9200.0},
                            {"name": "Draw", "price": 3.60, "available": 7038.89},
                            {"name": "Panama", "price": 3.35, "available": 6100.0},
                        ],
                    }
                ],
            },
        ],
    },
    {
        "home_team": "Sweden",
        "away_team": "Norway",
        "commence_time": "2026-06-20T19:45:00Z",
        "bookmakers": [
            {
                "key": "svenskaspel_se",
                "title": "Svenska Spel",
                "last_update": "2026-06-16T12:03:00Z",
                "markets": [
                    {
                        "key": "h2h",
                        "outcomes": [
                            {"name": "Sweden", "price": 2.05},
                            {"name": "Draw", "price": 3.30},
                            {"name": "Norway", "price": 3.95},
                        ],
                    }
                ],
            },
            {
                "key": "nordicbet",
                "title": "NordicBet",
                "last_update": "2026-06-16T12:04:00Z",
                "markets": [
                    {
                        "key": "h2h",
                        "outcomes": [
                            {"name": "Sweden", "price": 2.08},
                            {"name": "Draw", "price": 3.35},
                            {"name": "Norway", "price": 3.85},
                        ],
                    }
                ],
            },
            {
                "key": "smarkets",
                "title": "Smarkets",
                "last_update": "2026-06-16T12:05:00Z",
                "markets": [
                    {
                        "key": "h2h_lay",
                        "outcomes": [
                            {"name": "Sweden", "price": 2.12, "available": 12400.0},
                            {"name": "Draw", "price": 3.45, "available": 5400.0},
                            {"name": "Norway", "price": 4.10, "available": 3700.0},
                        ],
                    }
                ],
            },
        ],
    },
]


@dataclass(frozen=True)
class BetResult:
    """Common result shape used by all calculator modes."""

    lay_stake: float
    liability: float
    profit_if_back_wins: float
    profit_if_lay_wins: float
    difference: float
    rating: float


@dataclass(frozen=True)
class PartLay:
    """A single partial lay position at one exchange price."""

    lay_odds: float
    amount: float


@dataclass(frozen=True)
class PartLayResult:
    """Aggregated result for several partial lay positions."""

    total_lay_stake: float
    weighted_average_lay_odds: float
    total_liability: float


@dataclass(frozen=True)
class OddsmatcherOpportunity:
    """A bookmaker back price matched against a Smarkets lay price."""

    event: str
    commence_time: str
    selection: str
    bookmaker: str
    bookmaker_key: str
    bookmaker_last_update: str
    exchange_last_update: str
    back_odds: float
    lay_odds: float
    lay_available: Optional[float]
    rating: float
    lay_stake: float
    liability: float
    profit_if_back_wins: float
    profit_if_lay_wins: float


def commission_decimal(commission_percent: float) -> float:
    """Convert a percentage such as 2.0 into a decimal such as 0.02."""
    return commission_percent / 100


def format_money(value: float, currency_symbol: str) -> str:
    """Format a money value with two decimals and the selected currency."""
    return f"{value:,.2f} {currency_symbol}"


def format_percent(value: float) -> str:
    """Format a percentage value with two decimals."""
    return f"{value:,.2f}%"


def configured_odds_api_key() -> str:
    """Read The Odds API key from Streamlit secrets or an environment variable."""
    try:
        secret_value = st.secrets.get("THE_ODDS_API_KEY", "")
    except Exception:
        secret_value = ""
    return str(secret_value or os.getenv("THE_ODDS_API_KEY", ""))


def validate_inputs(
    back_stake: float,
    back_odds: float,
    bookmaker_commission_percent: float,
    lay_odds: float,
    lay_commission_percent: float,
) -> List[str]:
    """Return validation errors for the shared calculator inputs."""
    errors: List[str] = []

    if back_stake <= 0:
        errors.append("Back stake must be positive.")
    if back_odds <= 1:
        errors.append("Back odds must be greater than 1.")
    if lay_odds <= 1:
        errors.append("Lay odds must be greater than 1.")
    if not 0 <= bookmaker_commission_percent <= 100:
        errors.append("Bookmaker commission must be between 0 and 100%.")
    if not 0 <= lay_commission_percent <= 100:
        errors.append("Lay commission must be between 0 and 100%.")

    return errors


def calculate_normal_bet(
    back_stake: float,
    back_odds: float,
    bookmaker_commission: float,
    lay_odds: float,
    lay_commission: float,
) -> BetResult:
    """
    Calculate a standard matched bet.

    The lay stake balances both outcomes by comparing:
    - bookmaker win profit, after optional bookmaker commission
    - exchange lay win return, after exchange commission
    """
    bookmaker_win_profit = back_stake * (back_odds - 1) * (1 - bookmaker_commission)
    lay_stake = (back_stake + bookmaker_win_profit) / (lay_odds - lay_commission)
    liability = lay_stake * (lay_odds - 1)

    profit_if_back_wins = bookmaker_win_profit - liability
    profit_if_lay_wins = lay_stake * (1 - lay_commission) - back_stake
    difference = abs(profit_if_back_wins - profit_if_lay_wins)
    rating = (back_odds / lay_odds) * 100

    return BetResult(
        lay_stake=lay_stake,
        liability=liability,
        profit_if_back_wins=profit_if_back_wins,
        profit_if_lay_wins=profit_if_lay_wins,
        difference=difference,
        rating=rating,
    )


def calculate_free_bet_snr(
    back_stake: float,
    back_odds: float,
    bookmaker_commission: float,
    lay_odds: float,
    lay_commission: float,
) -> BetResult:
    """
    Calculate a Free Bet SNR (Stake Not Returned).

    SNR only pays the winnings portion at the bookmaker, so the stake is not
    included in the bookmaker return.
    """
    free_bet_stake = back_stake
    gross_bookmaker_profit = free_bet_stake * (back_odds - 1)
    bookmaker_win_profit = gross_bookmaker_profit * (1 - bookmaker_commission)

    # Required SNR formula: lay stake = free bet winnings / net lay odds.
    lay_stake = gross_bookmaker_profit / (lay_odds - lay_commission)
    liability = lay_stake * (lay_odds - 1)

    profit_if_back_wins = bookmaker_win_profit - liability
    profit_if_lay_wins = lay_stake * (1 - lay_commission)
    difference = abs(profit_if_back_wins - profit_if_lay_wins)
    conversion = min(profit_if_back_wins, profit_if_lay_wins) / free_bet_stake * 100

    return BetResult(
        lay_stake=lay_stake,
        liability=liability,
        profit_if_back_wins=profit_if_back_wins,
        profit_if_lay_wins=profit_if_lay_wins,
        difference=difference,
        rating=conversion,
    )


def calculate_free_bet_sr(
    back_stake: float,
    back_odds: float,
    bookmaker_commission: float,
    lay_odds: float,
    lay_commission: float,
) -> BetResult:
    """
    Calculate a Free Bet SR (Stake Returned).

    SR pays the bonus stake back as part of the bookmaker return, so it behaves
    like a normal back bet where the user did not pay cash for the stake.
    """
    free_bet_stake = back_stake
    bookmaker_win_profit = free_bet_stake * back_odds * (1 - bookmaker_commission)
    lay_stake = bookmaker_win_profit / (lay_odds - lay_commission)
    liability = lay_stake * (lay_odds - 1)

    profit_if_back_wins = bookmaker_win_profit - liability
    profit_if_lay_wins = lay_stake * (1 - lay_commission)
    difference = abs(profit_if_back_wins - profit_if_lay_wins)
    conversion = min(profit_if_back_wins, profit_if_lay_wins) / free_bet_stake * 100

    return BetResult(
        lay_stake=lay_stake,
        liability=liability,
        profit_if_back_wins=profit_if_back_wins,
        profit_if_lay_wins=profit_if_lay_wins,
        difference=difference,
        rating=conversion,
    )


def calculate_risk_free_bet(
    back_stake: float,
    back_odds: float,
    bookmaker_commission: float,
    lay_odds: float,
    lay_commission: float,
) -> BetResult:
    """
    Calculate a risk free bet.

    This uses the same hedge as a normal qualifying bet. If the bookmaker bet
    loses, the displayed lay-win outcome is the current cash result before any
    later refund or free bet conversion.
    """
    return calculate_normal_bet(
        back_stake=back_stake,
        back_odds=back_odds,
        bookmaker_commission=bookmaker_commission,
        lay_odds=lay_odds,
        lay_commission=lay_commission,
    )


def calculate_rating(
    back_stake: float,
    back_odds: float,
    bookmaker_commission: float,
    lay_odds: float,
    lay_commission: float,
) -> BetResult:
    """Calculate rating-focused values using the normal matched bet formula."""
    return calculate_normal_bet(
        back_stake=back_stake,
        back_odds=back_odds,
        bookmaker_commission=bookmaker_commission,
        lay_odds=lay_odds,
        lay_commission=lay_commission,
    )


def calculate_part_lays(part_lays: List[PartLay]) -> PartLayResult:
    """
    Calculate weighted average lay odds and total liability for part-lays.

    Each partial lay contributes stake * odds to the average and
    stake * (odds - 1) to the liability.
    """
    total_lay_stake = sum(part_lay.amount for part_lay in part_lays)
    if total_lay_stake <= 0:
        return PartLayResult(
            total_lay_stake=0,
            weighted_average_lay_odds=0,
            total_liability=0,
        )

    weighted_average_lay_odds = (
        sum(part_lay.lay_odds * part_lay.amount for part_lay in part_lays)
        / total_lay_stake
    )
    total_liability = sum(
        part_lay.amount * (part_lay.lay_odds - 1) for part_lay in part_lays
    )

    return PartLayResult(
        total_lay_stake=total_lay_stake,
        weighted_average_lay_odds=weighted_average_lay_odds,
        total_liability=total_liability,
    )


def fetch_json(url: str, params: Dict[str, Any]) -> Any:
    """Fetch JSON from an HTTP API using only the Python standard library."""
    query = urlencode({key: value for key, value in params.items() if value not in ("", None)})
    request = Request(f"{url}?{query}", headers={"User-Agent": "matched-betting-calculator"})

    try:
        with urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"The Odds API returned HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"Could not reach The Odds API: {exc.reason}") from exc


@st.cache_data(ttl=60 * 60)
def fetch_sports(api_key: str) -> List[Dict[str, Any]]:
    """Fetch active sports from The Odds API."""
    sports = fetch_json(f"{THE_ODDS_API_BASE_URL}/sports", {"apiKey": api_key})
    return [sport for sport in sports if sport.get("active")]


@st.cache_data(ttl=60)
def fetch_odds(
    api_key: str,
    sport_key: str,
    bookmaker_keys: List[str],
    include_bet_limits: bool,
) -> List[Dict[str, Any]]:
    """Fetch bookmaker odds and Smarkets lay odds from The Odds API."""
    requested_bookmakers = sorted(set(bookmaker_keys + ["smarkets"]))
    params = {
        "apiKey": api_key,
        "bookmakers": ",".join(requested_bookmakers),
        "markets": "h2h",
        "oddsFormat": "decimal",
        "dateFormat": "iso",
        "includeBetLimits": str(include_bet_limits).lower(),
    }
    return fetch_json(f"{THE_ODDS_API_BASE_URL}/sports/{sport_key}/odds", params)


def normalize_selection_name(name: str) -> str:
    """Normalize team/selection names so bookmaker and exchange outcomes can match."""
    return " ".join(name.lower().strip().split())


def bookmaker_label(bookmaker_key: str) -> str:
    """Return a readable bookmaker label for a key."""
    for bookmakers in BOOKMAKERS_BY_REGION.values():
        if bookmaker_key in bookmakers:
            return bookmakers[bookmaker_key]
    return bookmaker_key


def market_by_key(bookmaker: Dict[str, Any], market_key: str) -> Optional[Dict[str, Any]]:
    """Find one market inside a bookmaker object."""
    for market in bookmaker.get("markets", []):
        if market.get("key") == market_key:
            return market
    return None


def outcome_available_amount(outcome: Dict[str, Any]) -> Optional[float]:
    """Read available exchange size when the API provider includes it."""
    for key in ("bet_limit", "limit", "available", "available_amount"):
        value = outcome.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    return None


def calculate_opportunity_result(
    calculator_mode: str,
    stake: float,
    back_odds: float,
    lay_odds: float,
    lay_commission: float,
) -> BetResult:
    """Calculate the matched result for one oddsmatcher row."""
    calculators = {
        "Normal matched bet": calculate_normal_bet,
        "Free Bet SNR (Stake Not Returned)": calculate_free_bet_snr,
        "Free Bet SR (Stake Returned)": calculate_free_bet_sr,
    }
    return calculators[calculator_mode](
        back_stake=stake,
        back_odds=back_odds,
        bookmaker_commission=0,
        lay_odds=lay_odds,
        lay_commission=lay_commission,
    )


def estimate_odds_api_credits(bookmaker_count: int, market_count: int = 1) -> int:
    """
    Estimate The Odds API credit cost for bookmaker-filtered odds requests.

    The Odds API treats each group of up to 10 requested bookmakers like one
    region. Cost is markets requested multiplied by these bookmaker groups.
    """
    if bookmaker_count <= 0 or market_count <= 0:
        return 0
    bookmaker_groups = math.ceil(bookmaker_count / 10)
    return bookmaker_groups * market_count


def build_oddsmatcher_opportunities(
    odds_events: List[Dict[str, Any]],
    selected_bookmakers: List[str],
    calculator_mode: str,
    stake: float,
    lay_commission: float,
    minimum_rating: float,
) -> List[OddsmatcherOpportunity]:
    """Match bookmaker back odds against Smarkets lay odds for each event outcome."""
    opportunities: List[OddsmatcherOpportunity] = []

    for event in odds_events:
        event_name = f"{event.get('home_team', '')} v {event.get('away_team', '')}".strip(" v")
        smarkets = next(
            (
                bookmaker
                for bookmaker in event.get("bookmakers", [])
                if bookmaker.get("key") == "smarkets"
            ),
            None,
        )
        if smarkets is None:
            continue

        lay_market = market_by_key(smarkets, "h2h_lay") or market_by_key(smarkets, "h2h")
        if lay_market is None:
            continue

        lay_outcomes = {
            normalize_selection_name(outcome.get("name", "")): outcome
            for outcome in lay_market.get("outcomes", [])
            if isinstance(outcome.get("price"), (int, float))
        }

        for bookmaker in event.get("bookmakers", []):
            bookmaker_key = bookmaker.get("key", "")
            if bookmaker_key not in selected_bookmakers or bookmaker_key == "smarkets":
                continue

            back_market = market_by_key(bookmaker, "h2h")
            if back_market is None:
                continue

            for back_outcome in back_market.get("outcomes", []):
                back_odds = back_outcome.get("price")
                if not isinstance(back_odds, (int, float)):
                    continue

                lay_outcome = lay_outcomes.get(
                    normalize_selection_name(back_outcome.get("name", ""))
                )
                if lay_outcome is None:
                    continue

                lay_odds = lay_outcome.get("price")
                if not isinstance(lay_odds, (int, float)) or lay_odds <= 1:
                    continue

                result = calculate_opportunity_result(
                    calculator_mode=calculator_mode,
                    stake=stake,
                    back_odds=float(back_odds),
                    lay_odds=float(lay_odds),
                    lay_commission=lay_commission,
                )
                if result.rating < minimum_rating:
                    continue

                opportunities.append(
                    OddsmatcherOpportunity(
                        event=event_name,
                        commence_time=event.get("commence_time", ""),
                        selection=back_outcome.get("name", ""),
                        bookmaker=bookmaker_label(bookmaker_key),
                        bookmaker_key=bookmaker_key,
                        bookmaker_last_update=bookmaker.get("last_update", ""),
                        exchange_last_update=smarkets.get("last_update", ""),
                        back_odds=float(back_odds),
                        lay_odds=float(lay_odds),
                        lay_available=outcome_available_amount(lay_outcome),
                        rating=result.rating,
                        lay_stake=result.lay_stake,
                        liability=result.liability,
                        profit_if_back_wins=result.profit_if_back_wins,
                        profit_if_lay_wins=result.profit_if_lay_wins,
                    )
                )

    return sorted(opportunities, key=lambda item: item.rating, reverse=True)


def show_result_metrics(result: BetResult, currency_symbol: str) -> None:
    """Render the main result cards."""
    first_row = st.columns(3)
    second_row = st.columns(3)

    first_row[0].metric(
        "Recommended lay stake",
        format_money(result.lay_stake, currency_symbol),
    )
    first_row[1].metric(
        "Exchange liability",
        format_money(result.liability, currency_symbol),
    )
    first_row[2].metric("Rating", format_percent(result.rating))

    second_row[0].metric(
        "Profit if bookmaker bet wins",
        format_money(result.profit_if_back_wins, currency_symbol),
    )
    second_row[1].metric(
        "Profit if exchange lay wins",
        format_money(result.profit_if_lay_wins, currency_symbol),
    )
    second_row[2].metric(
        "Difference between outcomes",
        format_money(result.difference, currency_symbol),
    )


def render_calculator() -> None:
    """Build and run the calculator interface."""
    modes = [
        "Normal matched bet",
        "Free Bet SNR (Stake Not Returned)",
        "Free Bet SR (Stake Returned)",
        "Risk Free Bet",
        "Rating calculator",
    ]

    with st.sidebar:
        st.header("Bet setup")
        mode = st.selectbox("Bet type / calculator mode", modes)
        currency_symbol = st.text_input("Currency symbol", value="kr")
        currency = currency_symbol.strip() or "kr"

    input_col_1, input_col_2, input_col_3 = st.columns(3)

    with input_col_1:
        back_stake = st.number_input(
            "Back stake",
            min_value=0.0,
            value=1500.0,
            step=50.0,
            format="%.2f",
        )
        back_odds = st.number_input(
            "Back odds",
            min_value=1.01,
            value=2.0,
            step=0.01,
            format="%.2f",
        )

    with input_col_2:
        bookmaker_commission_percent = st.number_input(
            "Bookmaker commission %",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=0.1,
            format="%.2f",
        )
        lay_odds = st.number_input(
            "Lay odds",
            min_value=1.01,
            value=2.08,
            step=0.01,
            format="%.2f",
        )

    with input_col_3:
        lay_commission_percent = st.number_input(
            "Lay commission %",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=0.1,
            format="%.2f",
        )

    validation_errors = validate_inputs(
        back_stake=back_stake,
        back_odds=back_odds,
        bookmaker_commission_percent=bookmaker_commission_percent,
        lay_odds=lay_odds,
        lay_commission_percent=lay_commission_percent,
    )

    if validation_errors:
        for error in validation_errors:
            st.error(error)
        return

    bookmaker_commission = commission_decimal(bookmaker_commission_percent)
    lay_commission = commission_decimal(lay_commission_percent)

    calculators = {
        "Normal matched bet": calculate_normal_bet,
        "Free Bet SNR (Stake Not Returned)": calculate_free_bet_snr,
        "Free Bet SR (Stake Returned)": calculate_free_bet_sr,
        "Risk Free Bet": calculate_risk_free_bet,
        "Rating calculator": calculate_rating,
    }

    result = calculators[mode](
        back_stake=back_stake,
        back_odds=back_odds,
        bookmaker_commission=bookmaker_commission,
        lay_odds=lay_odds,
        lay_commission=lay_commission,
    )

    st.divider()
    st.subheader("Results")
    show_result_metrics(result, currency)

    if mode == "Normal matched bet":
        st.info(
            "Overall qualifying loss/profit: "
            f"{format_money(min(result.profit_if_back_wins, result.profit_if_lay_wins), currency)}"
        )
    elif mode in {"Free Bet SNR (Stake Not Returned)", "Free Bet SR (Stake Returned)"}:
        st.info(
            "Approximate conversion value: "
            f"{format_percent(result.rating)} of the free bet stake."
        )
    elif mode == "Risk Free Bet":
        st.info(
            "Risk free bet note: the lay-win result is shown before any later "
            "bookmaker refund or free bet conversion."
        )

    with st.expander("Advanced: multiple part-lays"):
        st.write(
            "Enter each partial lay amount at its available lay odds to estimate "
            "the weighted average lay odds and total exchange liability."
        )

        part_lay_count = st.number_input(
            "Number of part-lays",
            min_value=1,
            max_value=10,
            value=2,
            step=1,
        )

        part_lays: List[PartLay] = []
        part_lay_errors: List[str] = []

        for index in range(part_lay_count):
            odds_col, amount_col = st.columns(2)
            with odds_col:
                part_lay_odds = st.number_input(
                    f"Part-lay {index + 1} odds",
                    min_value=1.01,
                    value=lay_odds if index == 0 else lay_odds + 0.02,
                    step=0.01,
                    format="%.2f",
                    key=f"part_lay_odds_{index}",
                )
            with amount_col:
                default_amount = result.lay_stake / part_lay_count
                part_lay_amount = st.number_input(
                    f"Part-lay {index + 1} available amount",
                    min_value=0.0,
                    value=default_amount,
                    step=50.0,
                    format="%.2f",
                    key=f"part_lay_amount_{index}",
                )

            if part_lay_odds <= 1:
                part_lay_errors.append(f"Part-lay {index + 1} odds must be greater than 1.")
            if part_lay_amount < 0:
                part_lay_errors.append(f"Part-lay {index + 1} amount cannot be negative.")

            part_lays.append(PartLay(lay_odds=part_lay_odds, amount=part_lay_amount))

        if part_lay_errors:
            for error in part_lay_errors:
                st.error(error)
        else:
            part_lay_result = calculate_part_lays(part_lays)
            part_lay_cols = st.columns(3)
            part_lay_cols[0].metric(
                "Total part-lay stake",
                format_money(part_lay_result.total_lay_stake, currency),
            )
            part_lay_cols[1].metric(
                "Weighted average lay odds",
                f"{part_lay_result.weighted_average_lay_odds:,.2f}",
            )
            part_lay_cols[2].metric(
                "Total liability",
                format_money(part_lay_result.total_liability, currency),
            )


def render_oddsmatcher_results(
    opportunities: List[OddsmatcherOpportunity],
    result_summary: str,
) -> None:
    """Render stored or freshly fetched oddsmatcher results."""
    st.divider()
    st.caption(result_summary)
    st.write(f"Found {len(opportunities)} matched opportunities.")

    if not opportunities:
        st.warning(
            "No matching Smarkets lay prices were found for the selected bookmakers "
            "and sport. Try another sport, fewer filters, or check that Smarkets is "
            "available for those events."
        )
        return

    table_rows = [
        {
            "Event": opportunity.event,
            "Start": opportunity.commence_time,
            "Selection": opportunity.selection,
            "Bookmaker": opportunity.bookmaker,
            "Bookmaker updated": opportunity.bookmaker_last_update,
            "Back odds": round(opportunity.back_odds, 3),
            "Smarkets updated": opportunity.exchange_last_update,
            "Smarkets lay odds": round(opportunity.lay_odds, 3),
            "Lay available": (
                ""
                if opportunity.lay_available is None
                else round(opportunity.lay_available, 2)
            ),
            "Rating %": round(opportunity.rating, 2),
            "Lay stake": round(opportunity.lay_stake, 2),
            "Liability": round(opportunity.liability, 2),
            "Back wins": round(opportunity.profit_if_back_wins, 2),
            "Lay wins": round(opportunity.profit_if_lay_wins, 2),
        }
        for opportunity in opportunities
    ]

    st.dataframe(table_rows, use_container_width=True, hide_index=True)

    best = opportunities[0]
    st.subheader("Best result")
    best_cols = st.columns(4)
    best_cols[0].metric("Rating", format_percent(best.rating))
    best_cols[1].metric("Back odds", f"{best.back_odds:,.2f}")
    best_cols[2].metric("Lay odds", f"{best.lay_odds:,.2f}")
    best_cols[3].metric("Lay stake", format_money(best.lay_stake, "kr"))

    st.info(
        "This version can use Smarkets prices exposed through The Odds API. "
        "Direct Smarkets Trading API order-book liquidity is still the next upgrade."
    )


def render_oddsmatcher() -> None:
    """Render an oddsmatcher using bookmaker odds plus Smarkets lay prices."""
    st.subheader("Oddsmatcher")
    st.caption(
        "Match bookmaker back odds against Smarkets lay prices. Live data needs "
        "a The Odds API key; demo data is available without one."
    )

    data_source = st.radio(
        "Data source",
        ["Demo data", "Live: The Odds API"],
        horizontal=True,
    )

    api_key = ""
    sports = DEMO_SPORTS
    if data_source == "Live: The Odds API":
        api_key = st.text_input(
            "The Odds API key",
            value=configured_odds_api_key(),
            type="password",
            help=(
                "Paste a key here or set THE_ODDS_API_KEY before running Streamlit. "
                "Live bookmaker odds cannot be loaded without this key."
            ),
        )

        if api_key:
            try:
                sports = fetch_sports(api_key)
            except RuntimeError as exc:
                st.error(str(exc))
                return

            if not sports:
                st.warning("No active sports were returned by The Odds API.")
                return
        else:
            st.info(
                "Live mode requires a The Odds API key. Switch to Demo data to try "
                "the oddsmatcher layout without credentials."
            )

    sport_options = {
        f"{sport.get('group', 'Sport')} - {sport.get('title', sport.get('key'))}": sport["key"]
        for sport in sports
        if sport.get("key")
    }

    setup_col_1, setup_col_2, setup_col_3 = st.columns(3)
    with setup_col_1:
        sport_label = st.selectbox("Sport", list(sport_options.keys()))
        calculator_mode = st.selectbox(
            "Opportunity type",
            [
                "Normal matched bet",
                "Free Bet SNR (Stake Not Returned)",
                "Free Bet SR (Stake Returned)",
            ],
        )
    with setup_col_2:
        oddsmatcher_stake = st.number_input(
            "Stake / free bet stake",
            min_value=1.0,
            value=1000.0,
            step=50.0,
            format="%.2f",
        )
        lay_commission_percent = st.number_input(
            "Smarkets commission %",
            min_value=0.0,
            max_value=100.0,
            value=2.0,
            step=0.1,
            format="%.2f",
        )
    with setup_col_3:
        minimum_rating = st.number_input(
            "Minimum rating %",
            min_value=0.0,
            value=0.0,
            step=1.0,
            format="%.2f",
        )
        include_bet_limits = st.checkbox(
            "Request exchange availability",
            value=True,
            help="The Odds API may include bet limits for exchange prices when available.",
            disabled=data_source == "Demo data",
        )

    st.markdown("**Bookmakers with Swedish market keys**")
    st.caption(
        "Only The Odds API bookmaker keys for Sweden are shown here. Smarkets is "
        "added separately as the exchange source."
    )

    bookmaker_labels = {
        f"{label} ({key})": key
        for key, label in sorted(SWEDISH_LICENSED_BOOKMAKERS.items())
    }

    selected_bookmaker_labels = st.multiselect(
        "Swedish bookmakers",
        list(bookmaker_labels.keys()),
        default=list(bookmaker_labels.keys()),
    )
    selected_bookmakers = [
        bookmaker_labels[label] for label in selected_bookmaker_labels
    ]

    if len(selected_bookmakers) > 10:
        st.warning(
            "The Odds API charges usage by bookmaker groups. Selecting many bookmakers "
            "can use more quota."
        )

    requested_bookmaker_count = len(set(selected_bookmakers + ["smarkets"]))
    estimated_cost = estimate_odds_api_credits(
        bookmaker_count=requested_bookmaker_count,
        market_count=1,
    )
    if data_source == "Live: The Odds API":
        st.info(
            "Estimated API cost for one fetch: "
            f"{estimated_cost} credit(s). "
            f"With 500 monthly credits, that is about {500 // max(estimated_cost, 1)} "
            "similar fetches per month."
        )
        if st.button("Clear cached odds"):
            fetch_odds.clear()
            st.success("Cached odds cleared. The next live fetch will call the API again.")

    if st.button("Clear displayed results"):
        st.session_state.pop("oddsmatcher_opportunities", None)
        st.session_state.pop("oddsmatcher_result_summary", None)
        st.success("Displayed oddsmatcher results cleared.")
        return

    button_label = (
        "Load demo oddsmatcher results"
        if data_source == "Demo data"
        else "Fetch live oddsmatcher results"
    )
    fetch_clicked = st.button(button_label, type="primary")
    if not fetch_clicked:
        saved_opportunities = st.session_state.get("oddsmatcher_opportunities")
        saved_summary = st.session_state.get("oddsmatcher_result_summary")
        if saved_opportunities is not None and saved_summary:
            render_oddsmatcher_results(
                opportunities=saved_opportunities,
                result_summary=saved_summary,
            )
        return

    if not selected_bookmakers:
        st.error("Select at least one bookmaker.")
        return

    if data_source == "Live: The Odds API":
        if not api_key:
            st.error("Enter a The Odds API key before fetching live results.")
            return

        try:
            odds_events = fetch_odds(
                api_key=api_key,
                sport_key=sport_options[sport_label],
                bookmaker_keys=selected_bookmakers,
                include_bet_limits=include_bet_limits,
            )
        except RuntimeError as exc:
            st.error(str(exc))
            return
    else:
        odds_events = DEMO_ODDS_EVENTS

    opportunities = build_oddsmatcher_opportunities(
        odds_events=odds_events,
        selected_bookmakers=selected_bookmakers,
        calculator_mode=calculator_mode,
        stake=oddsmatcher_stake,
        lay_commission=commission_decimal(lay_commission_percent),
        minimum_rating=minimum_rating,
    )

    fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    result_summary = (
        f"Showing last fetched results from {fetched_at}. "
        f"Source: {data_source}. Sport: {sport_label}. "
        f"Bookmakers: {len(selected_bookmakers)}. Mode: {calculator_mode}."
    )
    st.session_state["oddsmatcher_opportunities"] = opportunities
    st.session_state["oddsmatcher_result_summary"] = result_summary

    render_oddsmatcher_results(
        opportunities=opportunities,
        result_summary=result_summary,
    )


def main() -> None:
    """Build and run the Streamlit app."""
    st.set_page_config(
        page_title="Matched Betting Calculator",
        page_icon="%",
        layout="wide",
    )

    st.title("Matched Betting Calculator")
    st.caption("A local Streamlit calculator and oddsmatcher for Swedish users.")

    calculator_tab, oddsmatcher_tab = st.tabs(["Calculator", "Oddsmatcher"])
    with calculator_tab:
        render_calculator()
    with oddsmatcher_tab:
        render_oddsmatcher()


if __name__ == "__main__":
    main()
