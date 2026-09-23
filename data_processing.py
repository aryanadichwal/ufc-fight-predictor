import pandas as pd

df = pd.read_csv('data/cleaned_ufc_data.csv')
df['date'] = pd.to_datetime(df['date'])

r_cols = [c for c in df.columns if c.startswith("R_")]
stat_suffixes = [c[2:] for c in r_cols]

def build_corner_rows(corner, opp_corner):
    cols = {
        'fight_id': df['ID'],
        'date': df['date'],
        'fighter': df[f'{corner}_fighter'],
        'opponent': df[f'{opp_corner}_fighter'],
        'won': (df['Winner'] == df[f'{corner}_fighter']).astype(int),
    }

    for suffix in stat_suffixes:
        cols[suffix] = df[f"{corner}_{suffix}"]

    return pd.DataFrame(cols)

red_rows = build_corner_rows("R","B")
blue_rows = build_corner_rows("B","R")

long_df = pd.concat([red_rows, blue_rows], ignore_index=True)
long_df = long_df.sort_values(["fighter","date"]).reset_index(drop=True)

roll_stats= ['won', 'SIG_STR_pct', 'TD_pct', 'CTRL', 'SUB_ATT', 'KD']
long_df["TD_pct"] = long_df["TD_pct"].fillna(0)
grouped = long_df.groupby("fighter")
for stat in roll_stats:
    shifted = grouped[stat].shift(1)
    long_df[f"{stat}_roll5"]  = (
        shifted.groupby(long_df["fighter"]).rolling(window=5, min_periods=1)
        .mean().reset_index(level=0, drop=True)
    )

roll_cols = [c for c in long_df.columns if c.endswith("_roll5")]
long_df = long_df.dropna(subset=roll_cols).reset_index(drop=True)

# print(long_df.head())

feature_cols = [c for c in long_df.columns if c.endswith("_roll5")]

left = long_df[["fight_id", "date", "fighter", "opponent", "won"]+feature_cols]
right =  long_df[["fight_id", "fighter"]+feature_cols].rename(
    columns={**{"fighter":"opponent"}, **{c:f"opp_{c}"for c in feature_cols}}
)

matchups = left.merge(right, on=["fight_id", "opponent"], how="inner")

for c in feature_cols:
    matchups[f"{c}_diff"] = matchups[c] - matchups[f"opp_{c}"]


diff_cols = [f"{c}_diff"for c in feature_cols]