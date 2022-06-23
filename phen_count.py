import sys
import pandas as pd

df = pd.read_csv(sys.argv[1], sep="\t", index_col=0)
c_mat = pd.DataFrame(data=0, index=df.index, columns=df.columns)

for i in df.index:
    for j in df.columns:
        if pd.isna(df.loc[i,j]):
            c_mat.loc[i, j] = 0
        else:
            c_mat.loc[i,j] = len(df.loc[i,j].split(","))

c_mat.to_csv(sys.argv[2], sep="\t")