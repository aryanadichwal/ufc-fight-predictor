import pandas as pd


def clean_ufc_data(raw_path):
    df = pd.read_csv(raw_path)
    df.index = df.index + 1
    df.index.name = 'ID'


    df1 = df.drop(columns=["Referee"])
    df1['date'] = pd.to_datetime(df1['date'])
    df1 = df1[df1["date"] >= "1999-07-17"]
    pd.set_option('display.max_columns', None)


    #Converting time to seconds
    time_cols =[col for col in df1.columns
                if df1[col].astype(str).str.match(r"^\d{1,2}:\d{2}$").any()] 

    for col in time_cols:
        df1[col] = df1[col].replace("-", pd.NA)
        df1[col] =  pd.to_timedelta("00:" + df1[col].astype("string"), errors="coerce").dt.total_seconds()

    
    #Spliting of columns
    of_cols = [col for col in df1.columns
            if df1[col].astype(str).str.contains(" of ").any()]
    
    for col in of_cols:
        split = df1[col].str.split(" of ", expand=True)
        base_name = col.replace(".", "")
        df1[base_name + "_Landed"] = split[0].astype(int)
        df1[base_name + "_Attempted"] = split[1].astype(int)
    df1 = df1.drop(columns=of_cols)


    #Handling % cols 
    pct_cols = [col for col in df1.columns if df1[col].astype(str).str.contains("%").any()]
    for col in pct_cols:
        df1[col] = df1[col].replace("---", pd.NA)
        df1[col] = df1[col].str.rstrip("%").astype("float")

    #DROPPING rows without any winner
    df1 = df1.dropna(subset=["Winner"])

    df1.to_csv("data/cleaned_ufc_data.csv")

    return df1



# clean_ufc_data("data/ufc-data.csv")



