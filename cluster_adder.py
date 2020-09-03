import pandas as pd

# Add the cluster column to the data.

# Output File.
new_cases_out_file = "new_cases.csv"
active_cases_out_file = "active_cases.csv"

# Open the cluster information.
cluster_info = pd.read_csv("./cluster_draft.csv")
cluster_info.columns = ['school', 'cluster', 'listed']

# Open the new cases file.
new_cases = pd.read_csv("./new_cases.csv")
new_cases = pd.merge(new_cases, cluster_info, on='school', how='inner')
new_cases.to_csv(new_cases_out_file,index=False)

# Open the active_cases file.
active_cases = pd.read_csv("./active_cases.csv")
active_cases = pd.merge(active_cases, cluster_info, on='school', how='inner')
active_cases.to_csv(active_cases_out_file,index=False)