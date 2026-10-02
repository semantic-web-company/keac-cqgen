import pandas

import pandas as pd

df = pd.read_csv('/Users/ivelina/Documents/dev/ttyg/KEAC-challenge/keac-cq-generation/skill_automate/data/gold_standard/benchmarkdataset_full.csv', sep=";")
df = df[df['Scenario'].astype(bool)]

df.to_csv("/Users/ivelina/Documents/dev/ttyg/KEAC-challenge/keac-cq-generation/skill_automate/data/gold_standard/benchmarkdataset_full_Scenario.csv",sep=",")

#print(df.to_string())
print(df.loc[768, 'Scenario'])