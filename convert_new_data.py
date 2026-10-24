"""Converts the newer 'merged_stats_n_scorecards' CSV into the column layout of the
original ufc-data.csv, so data_cleaning.py / data_processing.py / model.py / app.py
keep working without changes."""
import re
import pandas as pd

NEW_PATH = "data/merged_stats_n_scorecards.csv"
OLD_PATH = "data/ufc-data-2023.csv"   # optional: old file, used only to restore name casing
OUT_PATH = "data/ufc-data.csv"


def smart_title(name):
    """'SEAN O'MALLEY' -> "Sean O'Malley", 'CONOR MCGREGOR' -> 'Conor McGregor'."""
    out = []
    for w in str(name).strip().split():
        w = w.title()
        w = re.sub(r"^(Mc)([a-z])", lambda m: m.group(1) + m.group(2).upper(), w)
        w = re.sub(r"^(O')([a-z])", lambda m: m.group(1) + m.group(2).upper(), w)
        out.append(w)
    return " ".join(out)


def convert(new_path=NEW_PATH, old_path=OLD_PATH, out_path=OUT_PATH):
    n = pd.read_csv(new_path)

    # Name casing: reuse the exact spelling from the old dataset where we have it
    name_map = {}
    try:
        old = pd.read_csv(old_path)
        for col in ("R_fighter", "B_fighter"):
            for nm in old[col].dropna().unique():
                name_map[nm.upper()] = nm
    except FileNotFoundError:
        pass
    fix = lambda s: s.map(lambda x: name_map.get(str(x).strip().upper(), smart_title(x)))

    out = pd.DataFrame()
    out["R_fighter"] = fix(n["red_fighter_name"])
    out["B_fighter"] = fix(n["blue_fighter_name"])

    pairs = {            # old suffix -> new suffix
        "KD": "KD", "SIG_STR.": "sig_str", "SIG_STR_pct": "sig_str_pct",
        "TOTAL_STR.": "total_str", "TD": "TD", "TD_pct": "TD_pct",
        "SUB_ATT": "sub_att", "REV": "rev", "CTRL": "ctrl",
        "HEAD": "sig_str_head", "BODY": "sig_str_body", "LEG": "sig_str_leg",
        "DISTANCE": "sig_str_distance", "CLINCH": "sig_str_clinch", "GROUND": "sig_str_ground",
    }
    for old_s, new_s in pairs.items():
        for corner, word in (("R", "red"), ("B", "blue")):
            col = n[f"{word}_fighter_{new_s}"]
            if old_s in ("SIG_STR_pct", "TD_pct"):
                # new file has '75.0' / '---'; old format is '75%' / '---'
                num = pd.to_numeric(col, errors="coerce")
                col = num.round().map(lambda v: f"{int(v)}%" if pd.notna(v) else "---")
            out[f"{corner}_{old_s}"] = col

    out["win_by"] = n["method"]
    out["last_round"] = n["round"]
    out["last_round_time"] = n["time"]
    out["Format"] = n["time_format"]
    out["Referee"] = n["referee"]
    out["date"] = pd.to_datetime(n["event_date"], dayfirst=True).dt.strftime("%Y-%m-%d")
    out["location"] = n["event_location"]
    out["Fight_type"] = n["bout_type"]
    out["Winner"] = out["R_fighter"].where(n["fight_outcome"] == "red_win",
                    out["B_fighter"].where(n["fight_outcome"] == "blue_win"))

    out = out.sort_values("date", ascending=False).reset_index(drop=True)
    out.to_csv(out_path, index=False)
    return out


if __name__ == "__main__":
    df = convert()
    print(df.shape, df["date"].min(), "->", df["date"].max())
