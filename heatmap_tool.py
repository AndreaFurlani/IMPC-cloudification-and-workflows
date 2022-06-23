import sys
import pandas as pd
import numpy as np
from bokeh.io import save,show
from bokeh.models import ColorBar, ColumnDataSource, CategoricalColorMapper
from bokeh.plotting import figure
from bokeh.transform import transform
import bokeh.palettes


#Import data
threshold=int(sys.argv[3])
mat = pd.read_csv(sys.argv[1], sep="\t", index_col=0)
mat.index.name = 'MGI_id'
mat.columns.name = 'MGI_id_col'

#set diagonal to nan to avoid bias in display counting
mat=mat.astype(float)
np.fill_diagonal(mat.values,float('nan'))

#filtering phase
rem=[]
if threshold != 0:
    for i in mat.columns:
        if mat[i].max() < threshold:
            rem.append(i)
    mat.drop(rem,inplace=True,axis=1)
    mat.drop(rem,inplace=True,axis=0)

#Create a custom palette and add a specific mapper to map color with values (OLD METHOD, LABELS IN COLORBAR IN WRONG POSITION)
#df = mat.stack(dropna=False).rename("value").reset_index()
#my_pal = bokeh.palettes.diverging_palette(bokeh.palettes.Inferno256,bokeh.palettes.Viridis256,n=df.value.max()+1)
#mapper = LinearColorMapper(palette=my_pal, low=df.value.min(), high=df.value.max(), nan_color = 'gray')

#Create a custom palette and add a specific mapper to map color with values, we are converting them to strings to create a categorical color mapper to include only the
#values that we have in the matrix and retrieve a better representation
df = mat.stack(dropna=False).rename("value").reset_index()
fact = df.value.unique()
fact.sort()
fact = fact[0:len(fact)-1] #remove nan from labels
fact = fact.astype(str)
df.value = df.value.astype(str)

mapper = CategoricalColorMapper(palette=bokeh.palettes.inferno(len(df.value.unique())-1), factors= fact, nan_color = 'gray')


#Define a figure
p = figure(
    plot_width=800,
    plot_height=800,
    title="Heatmap",
    x_range=list(df.MGI_id.drop_duplicates()),
    y_range=list(df.MGI_id_col.drop_duplicates()[::-1]),
    tooltips=[('Gene','@MGI_id_col'),('Gene','@MGI_id'),('Common phenotypes','@value')],
    x_axis_location="above",
    output_backend="webgl")

#Create rectangles for heatmap
p.rect(
    x="MGI_id",
    y="MGI_id_col",
    width=1,
    height=1,
    source=ColumnDataSource(df),
    fill_color=transform('value', mapper))
p.xaxis.major_label_orientation = 45
#Add legend
color_bar = ColorBar(
    color_mapper=mapper,
    location=(0, 0),
    label_standoff=6,
    border_line_color=None)
p.add_layout(color_bar, 'right')

#Save html file
save(p, filename=sys.argv[2])