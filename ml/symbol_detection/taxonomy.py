"""
SIP Intelligence — Symbol Taxonomy Definitions
Categorized into Signals, Track & Signalling Equipment, and Kavach.
"""
from __future__ import annotations

import json
from pathlib import Path

SIGNALS = [
    "2A_CL", "3A_CL", "4A_CL", "HOME", "STARTER", "ADV_STARTER",
    "DISTANT", "IBS", "AUTO", "SEMI_AUTO", "CALL_ON", "SHUNT",
    "PL_SHUNT", "REPEATER", "ROUTE_IND", "CO_ACT", "GATE_SIG",
]

TRACK_EQUIPMENT = [
    "POINT", "X_OVER", "TRAP", "FPL", "FM", "IRJ", "TC", "AC",
    "DP", "OVL", "CSR", "LC", "CH", "SPT", "LOC", "RR_EI",
    "GF", "BUFFER", "SAND_HUMP",
]

KAVACH = [
    "KAVACH_N", "KAVACH_S", "KAVACH_T", "KAVACH_X", "KAVACH_D",
    "KAVACH_G", "KAVACH_L", "KAVACH_A", "TIN", "TAG_ID",
    "MAIN_DUP", "NOM_REV", "SK_ID", "RFID_CHAINAGE",
]

ALL_CLASSES = SIGNALS + TRACK_EQUIPMENT + KAVACH

CLASS_TO_IDX = {cls_name: idx for idx, cls_name in enumerate(ALL_CLASSES)}
IDX_TO_CLASS = {idx: cls_name for idx, cls_name in enumerate(ALL_CLASSES)}


def load_full_catalog(catalog_path: str = "data/symbols/symbols_catalog.json") -> dict:
    p = Path(catalog_path)
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"total_symbols": len(ALL_CLASSES), "symbols": []}

