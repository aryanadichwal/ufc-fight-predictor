"""Converts master.csv (one row per fight, numeric stats) into the column layout of the
original ufc-data.csv, so data_cleaning.py / data_processing.py / model.py / app.py
keep working unchanged.

master.csv also contains other promotions (Strikeforce, PRIDE, WEC, Contender Series,
Road to UFC...). Only UFC events are kept, so a fighter's "last 5 fights" are UFC fights."""
import re
import pandas as pd

MASTER_PATH = "data/master.csv"
OUT_PATH = "data/ufc-data.csv"

UFC_EVENT = re.compile(r"UFC|Ultimate Fighter|Ortiz vs Shamrock 3", re.I)
NOT_UFC = re.compile(r"Road to UFC|DWCS|Contender", re.I)


def of(landed, atmp):
    return landed.astype(int).astype(str) + " of " + atmp.astype(int).astype(str)


def pct(landed, atmp):
    p = (landed / atmp.where(atmp > 0) * 100).round()
    return p.map(lambda v: f"{int(v)}%" if pd.notna(v) else "---")


def mmss(sec):
    sec = sec.fillna(0).astype(int)
    return (sec // 60).astype(str) + ":" + (sec % 60).astype(str).str.zfill(2)


def convert(master_path=MASTER_PATH, out_path=OUT_PATH):
    m = pd.read_csv(master_path, low_memory=False)
    m = m[m["event_name"].str.contains(UFC_EVENT) & ~m["event_name"].str.contains(NOT_UFC)]
    m = m.drop_duplicates("fight_id").copy()

    out = pd.DataFrame(index=m.index)
    out["R_fighter"] = m["r_fighter_name"]
    out["B_fighter"] = m["b_fighter_name"]

    for c, w in (("R", "r"), ("B", "b")):
        t = f"{w}_total_"
        out[f"{c}_KD"] = m[t + "kd"]
    # keep the same column order as the old file
    cols = {}
    for c, w in (("R", "r"), ("B", "b")):
        t = f"{w}_total_"
        cols[f"{c}_SIG_STR."] = of(m[t + "sig_landed"], m[t + "sig_atmp"])
        cols[f"{c}_SIG_STR_pct"] = pct(m[t + "sig_landed"], m[t + "sig_atmp"])
        cols[f"{c}_TOTAL_STR."] = of(m[t + "total_str_landed"], m[t + "total_str_atmp"])
        cols[f"{c}_TD"] = of(m[t + "td_success"], m[t + "td_atmp"])
        cols[f"{c}_TD_pct"] = pct(m[t + "td_success"], m[t + "td_atmp"])
        cols[f"{c}_SUB_ATT"] = m[t + "sub_att"]
        cols[f"{c}_REV"] = m[t + "rev"]
        cols[f"{c}_CTRL"] = mmss(m[t + "ctrl_seconds"])
        for old, new in (("HEAD", "head"), ("BODY", "body"), ("LEG", "leg"),
                         ("DISTANCE", "distance"), ("CLINCH", "clinch"), ("GROUND", "ground")):
            cols[f"{c}_{old}"] = of(m[f"{t}sig_str_landed_{new}"], m[f"{t}sig_str_atmp_{new}"])

    order = ["KD", "SIG_STR.", "SIG_STR_pct", "TOTAL_STR.", "TD", "TD_pct", "SUB_ATT", "REV",
             "CTRL", "HEAD", "BODY", "LEG", "DISTANCE", "CLINCH", "GROUND"]
    for s in order:
        for c in ("R", "B"):
            out[f"{c}_{s}"] = out[f"{c}_{s}"] if s == "KD" else cols[f"{c}_{s}"]
    out = out[["R_fighter", "B_fighter"] + [f"{c}_{s}" for s in order for c in ("R", "B")]]

    out["win_by"] = m["method"]
    out["last_round"] = m["finish_round"]
    out["last_round_time"] = m["finish_time"]
    out["Format"] = m["time_format"]
    out["Referee"] = m["referee"]
    out["date"] = pd.to_datetime(m["event_date"]).dt.strftime("%Y-%m-%d")
    out["location"] = m["event_location"]
    out["Fight_type"] = m["weight_class"].fillna("") + m["title_fight"].map({1: " Title Bout"}).fillna(" Bout")
    out["Winner"] = out["R_fighter"].where(m["winner_id"] == m["r_fighter_id"],
                    out["B_fighter"].where(m["winner_id"] == m["b_fighter_id"]))

    out = out.sort_values("date", ascending=False).reset_index(drop=True)
    out.to_csv(out_path, index=False)
    return out


if __name__ == "__main__":
    df = convert()
    print(df.shape, df["date"].min(), "->", df["date"].max())
