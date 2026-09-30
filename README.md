# UFC Fight Predictor

A web app that predicts the winner of a UFC fight. Pick two fighters and it shows each fighter's win probability, who the favourite is, and a side-by-side comparison of the stats behind the prediction, so you can judge the fight yourself too.

The model is a logistic regression trained on each fighter's recent form (rolling average of their last 5 fights).

> **Note:** The dataset only covers fights up to **2023**. Newer fighters and recent form are not included, so predictions may be outdated or unavailable.

## Features

- Search and select two fighters from dropdowns (no exact-name typing needed)
- Win probability for each fighter with a red/blue split bar and the predicted favourite
- **Tale of the tape:** last-5-fight averages for both fighters, with the leader of each stat highlighted
- **Model impact:** a bar under each stat showing how strongly it pushed the prediction toward the red or blue corner
- Last fight date for each fighter, so you can spot stale form

## How it works

1. **Clean** the raw UFC data (time to seconds, split "X of Y" stats, handle % columns).
2. **Engineer features**: rolling 5-fight averages for win rate, significant strike %, takedown %, control time, submission attempts, and knockdowns. Each matchup uses the *difference* between the two fighters.
3. **Train** a logistic regression pipeline (StandardScaler + LogisticRegression) with a time-based 80/20 split, no shuffling.
4. **Predict** win probabilities for any two fighters in the dataset and explain them with per-stat model impact.

## Requirements

- Python 3.8+
- streamlit
- pandas
- scikit-learn

```bash
pip install -r requirements.txt
```

## Project structure

```
├── .streamlit/
│   └── config.toml           # dark theme settings
├── data/
│   └── ufc-data.csv          # raw data (you provide this)
├── app.py                    # Streamlit web app
├── data_cleaning.py          # cleans raw data -> data/cleaned_ufc_data.csv
├── data_processing.py        # builds rolling-form features and matchups
├── model.py                  # trains and evaluates the model
├── predict_interace.py       # optional command-line predictor
└── requirements.txt
```

## Usage

**1. Clean the data** (run once):

```bash
python -c "from data_cleaning import clean_ufc_data; clean_ufc_data('data/ufc-data.csv')"
```

This creates `data/cleaned_ufc_data.csv`, which the app reads.

**2. Run the app:**

```bash
python -m streamlit run app.py
```

It opens in your browser. Choose a fighter for each corner and click **Predict fight**.

**Optional: command-line version**

```bash
python predict_interace.py
```

Enter two fighter names exactly as they appear in the dataset.

## Deploying for free

The app can be hosted on [Streamlit Community Cloud](https://streamlit.io/cloud):

1. Push the project to a public GitHub repo, including `data/cleaned_ufc_data.csv` and `.streamlit/config.toml` (check they are not blocked by `.gitignore`).
2. Sign in at share.streamlit.io with GitHub.
3. Select the repo, set the main file to `app.py`, and deploy.

## Evaluating the model

In `model.py`, uncomment the print lines at the bottom to see the confusion matrix, classification report, and ROC-AUC.

## Limitations

- Data ends in 2023.
- Uses only 6 rolling stats; no weight class, reach, age, or opponent quality.
- Only fighters with at least 2 fights in the dataset can be selected.
- Predictions are for fun and analysis, not betting advice.
