import sys
import pandas as pd
from bokeh.io import save,show
from bokeh.models import ColorBar, ColumnDataSource, CategoricalColorMapper
from bokeh.plotting import figure
from bokeh.transform import transform
import bokeh.palettes


threshold=int(sys.argv[2])
mat = pd.read_csv(sys.argv[1], sep="\t", index_col=0)

mat.index.name = 'MGI_id'
mat.columns.name = 'phen_sys'

#filtering phase
rem=[]
if threshold != 0:
    for i in mat.index:
        if mat.loc[i].max() < threshold:
            rem.append(i)
    mat.drop(rem,inplace=True,axis=0)



#Create a custom palette and add a specific mapper to map color with values, we are converting them to strings to create a categorical color mapper to include only the
#values that we have in the matrix and retrieve a better representation
df = mat.stack(dropna=False).rename("value").reset_index()
fact= df.value.unique()
fact.sort()
fact = fact.astype(str)
df.value = df.value.astype(str)

mapper = CategoricalColorMapper(palette=bokeh.palettes.inferno(len(df.value.unique())), factors= fact, nan_color = 'gray')


#Define a figure
p = figure(
    plot_width=1280,
    plot_height=800,
    title="Heatmap",
    x_range=list(df.phen_sys.drop_duplicates()[::-1]),
    y_range=list(df.MGI_id.drop_duplicates()),
    tooltips=[('Phenotype system','@phen_sys'),('Gene','@MGI_id'),('Phenotypes','@value')],
    x_axis_location="above",
    output_backend="webgl")

#Create rectangles for heatmap
p.rect(
    x="phen_sys",
    y="MGI_id",
    width=1,
    height=1,
    source=ColumnDataSource(df),
    fill_color=transform('value', mapper))
p.xaxis.major_label_orientation = 45

#Add legend
color_bar = ColorBar(
    color_mapper=mapper,
    label_standoff=6,
    border_line_color=None)
p.add_layout(color_bar, 'right')

#Save html file
save(p, filename=sys.argv[3])