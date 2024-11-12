import csv
import json
import os
import pandas as pd

# Define the data as a multiline string for demonstration. In practice, this would come from a file.
data = pd.read_csv(os.path.join('data', 'prepared_data.csv'))

# Convert the CSV data to a list of dictionaries
json_data = data.to_dict(orient='records')

# Output the JSON
json_output = json.dumps(json_data, indent=4)

# Write the JSON data to a file
with open('prepared_data.json', 'w') as f:
    f.write(json_output)
