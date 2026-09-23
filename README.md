# UFC Fight Predictor

Predicts the winner of a UFC fight using a logistic regression model trained on each fighter's recent form (rolling average of their last 5 fights).

> **Note:** The dataset only covers fights up to **2023**. Fights after that are not included, so predictions for newer fighters or recent form may be outdated or unavailable.

## How it works

1. **Clean** the raw UFC data (time to seconds, split "X of Y" stats, handle % columns).
2. **Engineer features**: rolling 5-fight averages for win rate, significant strike %, takedown %, control time, submission attempts, and knockdowns. Each matchup uses the *difference* between the two fighters.
3. **Train** a logistic regression pipeline (time-based 80/20 split, no shuffling).
4. **Predict** win probabilities for any two fighters in the dataset.

## Requirements

- Python 3.8+
- pandas
- scikit-learn

```bash
pip install pandas scikit-learn
```

## Project structure

```
├── data/
│   └── ufc-data.csv          # raw data (you provide this)
├── data_cleaning.py          # cleans raw data -> data/cleaned_ufc_data.csv
├── data_processing.py        # builds rolling-form features and matchups
├── model.py                  # trains and evaluates the model
└── predict_interace.py       # CLI to predict a fight
```

## Usage

**1. Clean the data** (run once):

```bash
python -c "from data_cleaning import clean_ufc_data; clean_ufc_data('data/ufc-data.csv')"
```

**2. Predict a fight:**

```bash
python predict_interace.py
```

Enter two fighter names exactly as they appear in the dataset:

```
Enter Fighter 1: <name>
Enter Fighter 2: <name>
```

Output shows each fighter's win probability and the predicted favorite.

## Evaluating the model

In `model.py`, uncomment the print lines at the bottom to see the confusion matrix, classification report, and ROC-AUC.

## Limitations

- Data ends in 2023.
- Uses only 6 rolling stats; no weight class, reach, age, or opponent quality.
- Fighters need at least one prior fight in the dataset.
