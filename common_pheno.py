import sys
import pandas as pd

data = pd.read_csv(sys.argv[1], sep="\t")

#I need this since importing the elements of the second colum once imported are seen as a single string instead of being lists
data['MP term list'] = data['MP term list'].str.split(",").map(set)

#Intersection of the lists
cross = data[["MGI id", "MP term list"]].merge(data[["MGI id", "MP term list"]], how="cross")
cross["intersection"] = (cross.apply(lambda row: row["MP term list_x"].intersection(row["MP term list_y"]), axis=1).map(",".join).replace("",None))

p_mat = pd.read_csv(sys.argv[2], sep="\t", index_col=0)
c_mat = pd.read_csv(sys.argv[3], sep="\t", index_col=0)

#Saving the intersections in the matrix
p_mat = cross.pivot("MGI id_x", "MGI id_y", "intersection").rename_axis(None, axis=1).rename_axis(None)
p_mat = p_mat.reindex(data['MGI id']).reindex(data['MGI id'], axis=1)
del(cross)


#Count the number of elements instead of having the list
for i in p_mat:
    c_mat[i] = p_mat[i].str.split(",").apply(lambda s: 0 if s is None else len(s))

p_mat.to_csv(sys.argv[4], sep="\t")
c_mat.to_csv(sys.argv[5], sep="\t")