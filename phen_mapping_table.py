import pandas as pd

url = "https://raw.githubusercontent.com/obophenotype/upheno-dev/master/mappings/upheno_mapping_mp_hp.csv"
df = pd.read_csv(url,header=0)
df.drop(labels=["x","y","matching_category"], axis=1, inplace=True)
df.columns=["hpName","mpName","hpId","mpId"]
df.to_csv("tests/hp_mp_mapping.csv",header=True,index=False,index_label=False)