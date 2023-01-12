# Run this file in terminal: python run.py "<YOUR PIPE ID>"
# Your pipe id is in the URL (https://app.pipefy.com/pipes/<PIPE_ID>)

# Imports

import sys
import pipefy
import pandas as pd
import numpy as np
from datetime import datetime
import json

def main(pipe_id):
    # Set pipe ID to get data from Pipefy
    pipe = pipefy.Pipe(pipe_id)

    print("Getting cards data from Pipefy...")
    data = pipe.get_data()

    #['df_cards', 'df_current_phase', 'df_assignees', 'df_comments', 'df_labels', 'df_phases_history', 'df_fields']
    print("Turning the data returned from GraphQL into various dataframes")
    dfs = pipe.set_dataframes(data)

    print("Turn the column value in df_fields from string into a list type and then explode the list.")
    dfs["df_fields"] = pd.eval(f"value2 = dfs['df_fields']['value'].str.strip('[\"\"]').str.split('\", \"')", target=dfs["df_fields"])
    dfs["df_fields"] = dfs["df_fields"].explode("value2", ignore_index=True)
    dfs["df_fields"].drop(columns=["value"], inplace=True)

    print("Set the column phase in df_phases_history from dict into various columns")
    dfs["df_phases_history"] = pd.concat([dfs["df_phases_history"], dfs["df_phases_history"]["phase"].apply(pd.Series)], axis=1)
    dfs["df_phases_history"].drop(columns=["phase"], inplace=True)
    
    print("Saving the dataframes into CSV files.")
    for df in dfs:
        dfs[df].to_csv(f"../datasets/data_{df[3:len(df)]}.csv", index = False)
    
    print("Done!!!")

if __name__ == "__main__":
    main(sys.argv[1])

    #pipe_id = 302551116

