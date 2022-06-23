import sys
import pandas as pd

data = pd.read_csv(sys.argv[1], sep="\t")

phen_matrix = pd.DataFrame(index=data['MGI id'], columns=data['MGI id'])
count_matrix = pd.DataFrame(index=data['MGI id'], columns=data['MGI id'])

phen_matrix.to_csv(sys.argv[2], sep="\t")
count_matrix.to_csv(sys.argv[3], sep="\t")