import os
import pandas as pd
import tabula
import urllib.request
import urllib.error

# Output File.
new_cases_out_file = "new_cases.csv"
active_cases_out_file = "active_cases.csv"

# Column names
columns = ["school", "close_contact", "postive_case", "suspected_case", "total"]

# Prompt user for the file website address.
# Doesn't crash the most gracefully right now, but also
# shouldn't corrupt the CSV data file.
print("Please enter the web url for the PDF you'd like to add.")
try:
    file_path = input()
    req = urllib.request.urlopen(file_path)
except urllib.error.HTTPError as e:
    print("Are you sure the website exists?")
    exit()
except urllib.error.URLError as e:
    print("Are you sure the website exists?")
    exit()
except ValueError as e:
    print("Are you sure the url is valid?")
    exit()

# Use this to hardcode in the file to read.
# file_path = "/Users/moorejar/Desktop/8.27.2020-Local-School-COVID-19-Reporting-Daily-Report.eq.pdf"

# Read in Page 1, it contains two tables.
# Table 1: New Cases Reported for the District
# Table 2: New Cases Reported by School
# table = tabula.read_pdf(file_path, pages=1, multiple_tables=True)#, guess=True)

# Keep the district cases from Table 1
# district_cases = table[0]

# Keep the cases reported by school from Table 2
#school_cases = table[1]
#school_cases = school_cases.dropna(axis=1, how='all')
#print(school_cases)
#school_cases.columns = columns

#print(school_cases)

# Loop through the remaining pages to get the other
# school information.
#for p in range(2,6):
    # table = tabula.read_pdf(file_path, pages=p, guess=True)
    # table[0].columns = columns
    # school_cases = pd.concat([school_cases, table[0]],)

# Read the entire PDF.
# Break into the three tables.
table = tabula.read_pdf(file_path, pages='all', guess=True, multiple_tables=True)

# Keep the district cases from Table 0
district_cases = table[0]

# Merge the rest of the tables and then split them out at the location 
# of Total as the value in the School column.
# Otherwise tabula-py doesn't split them intelligently.
school_cases = pd.DataFrame(columns=columns)
for t in table[1:]:
    t = t.dropna(axis=1, how='all')
    t.columns = columns
    school_cases = pd.concat([school_cases, t],)

# Add a date column for the day's data.
school_cases['date'] = file_path.split("/")[-1].split("-")[0].replace(".","/")

# Reset the indexing for the school cases.
school_cases.reset_index(drop=True, inplace=True)

# Find rows that have "Total" in the school column.
# This separates new and active as it is dynamic 
# based on the day.
split_row = school_cases.index[school_cases['school'] == "Total"].tolist()[0] + 1
new_cases = school_cases.iloc[:split_row, :]
active_cases = school_cases.iloc[split_row:, :]

# Print out the data for review. (Debugging)
# print(new_cases)
# print("\n\n\n")
# print(active_cases)

# Open the cluster information.
cluster_info = pd.read_csv("./cluster_draft.csv")
cluster_info.columns = ['school', 'cluster', 'listed']

# Write the data out to a file.
# Want to avoid data duplication so will check 
# if that day of data exists in the dataframe before writing data out.
if os.path.exists(new_cases_out_file):
    # If data file exists, make sure we first don't have that 
    # date already recorded.
    # Not memory efficient, but this data file shouldn't be terribly large.
    new_cases_all_data = pd.read_csv(new_cases_out_file)
    if not school_cases['date'].unique()[0] in new_cases_all_data['date'].unique():
        new_cases = pd.merge(new_cases, cluster_info, on='school', how='inner')
        new_cases_all_data = pd.concat([new_cases_all_data, new_cases],)
        new_cases_all_data.to_csv(new_cases_out_file, index=False)
else:
    new_cases.to_csv(new_cases_out_file,index=False)

if os.path.exists(active_cases_out_file):
    # If data file exists, make sure we first don't have that 
    # date already recorded.
    # Not memory efficient, but this data file shouldn't be terribly large.
    active_cases_all_data = pd.read_csv(active_cases_out_file)
    if not school_cases['date'].unique()[0] in active_cases_all_data['date'].unique():
        active_cases = pd.merge(active_cases, cluster_info, on='school', how='inner')
        active_cases_all_data = pd.concat([active_cases_all_data, active_cases],)
        active_cases_all_data.to_csv(active_cases_out_file, index=False)
else:
    active_cases.to_csv(active_cases_out_file,index=False)    
    