import json
import os
import pandas as pd

data = pd.read_csv(os.path.join('data', 'prepared_data_3i.csv'))

json_data = data.to_dict(orient='records')

json_output = json.dumps(json_data, indent=4)

with open('prepared_data_3i.json', 'w') as f:
    f.write(json_output)
