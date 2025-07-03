from itertools import combinations
from typing import List, Dict, Any


def format_currency_pairs(currencies: List) -> Dict[str, Any]:
    pairs = []

    # all combinations of currencies
    for base_currency in currencies:
        for target_currency in currencies:
            # skip same currency pairs (e.g., EUR/EUR)
            if base_currency.id == target_currency.id:
                continue

            pair = {
                "code": f"{base_currency.code}{target_currency.code}",
                "name": f"{base_currency.name} / {target_currency.name}",
            }
            pairs.append(pair)

    return {"pairs": pairs}
