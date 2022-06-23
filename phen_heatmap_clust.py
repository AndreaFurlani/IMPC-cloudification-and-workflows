import sys
import seaborn as sns
import pandas as pd
import shutil

mat = pd.read_csv(sys.argv[1], sep="\t", index_col=0)
clust = str(sys.argv[2])
dist = str(sys.argv[3])
threshold = int(sys.argv[4])

mat.index.name = 'MGI_id'
mat.columns.name = 'phen_sys'

#filtering phase
rem=[]
if threshold != 0:
    for i in mat.index:
        if mat.loc[i].max() < threshold:
            rem.append(i)
    mat.drop(rem,inplace=True,axis=0)

if dist == '':
    dist='euclidean'

#Possible methods for clustering, docs here: https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html
#valid_clusts=["single","complete","average","weighted","centroid","median"]

s = sns.clustermap(mat,row_cluster=True,col_cluster=False, method=clust, metric=dist, cbar_pos=(0.01,0.01,0.01,0.2), cmap="magma")
s.savefig("output.png")
shutil.copyfile("output.png", sys.argv[5])