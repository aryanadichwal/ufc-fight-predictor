from data_processing import long_df, diff_cols
from model import log_reg_pipe
import pandas as pd

roll_stats = ['won', 'SIG_STR_pct', 'TD_pct', 'CTRL', 'SUB_ATT', 'KD']

def get_current_form(fighter_name, n=5):
    history = long_df[long_df['fighter'] == fighter_name].sort_values('date')
    if history.empty:
        return None
    return history[roll_stats].tail(n).mean()

def predict_fight(fighter1, fighter2, model=log_reg_pipe):
    form1 = get_current_form(fighter1)
    form2 = get_current_form(fighter2)

    if form1 is None:
        raise ValueError(f"No fight history found for '{fighter1}'")
    if form2 is None:
        raise ValueError(f"No fight history found for '{fighter2}'")

    diff_row = {}
    for stat in roll_stats:
        col_name = f"{stat}_roll5_diff"
        diff_row[col_name] = form1[stat] - form2[stat]

    X_new = pd.DataFrame([diff_row])[diff_cols]  
    prob1 = float(model.predict_proba(X_new)[0][1])  
    prob2 = 1 - prob1

    print(f'{fighter1:<20} {prob1*100:5.1f}%')
    print(f'{fighter2:<20} {prob2*100:5.1f}%')

    favorite = fighter1 if prob1 > prob2 else fighter2
    
    print(f"Favorite: {favorite}")
    
fighter1 = input("Enter Fighter 1: ")
fighter2 = input("Enter Fighter 2: ")



result = predict_fight(f"{fighter1}", f"{fighter2}")
