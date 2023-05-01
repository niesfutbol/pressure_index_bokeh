from jinja2 import Environment, FileSystemLoader
import pandas as pd
import numpy as np
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, ImageURL, HoverTool

url = "https://raw.githubusercontent.com/nepito/calculator-trs/develop/tests/data/logo_nies.png"

league = "135"
def assing_color_serie_a(x):
    if x < 7:
        return "blue"
    if x > 17:
        return "red"
    return "orange"


def assing_color_premier(x):
    if x < 6:
        return "blue"
    if x > 17:
        return "red"
    return "orange"


def assing_color_mx(x):
    if x < 5:
        return "blue"
    if x > 12:
        return "red"
    return "orange"

assing_color = {
    "262": assing_color_mx,
    "39": assing_color_premier,
    "263": assing_color_mx,
    "135": assing_color_serie_a
    }

bdp_and_ppda = pd.read_csv(f"/workdir/data/pression_index_{league}_2022.csv")
bdp_and_ppda["color"] = bdp_and_ppda["league"].map(assing_color[league])
source = ColumnDataSource(data=bdp_and_ppda)

TOOLTIPS = [
    ("Equipo", "@{team}"),
    ("Posición", "@{league}"),
    ("xG", "@{xG}"),
]
name_league = {
    "262": "Liga MX",
    "263": "Liga de Expansión MX",
    "39": "Premier League",
    "135": "Serie A",
    }
p = figure(
    title=f"PPDA vs BDP \n{name_league[league]} en el año 2022-2023",
    toolbar_location=None,
    sizing_mode="scale_both",
    aspect_ratio=2,
)

x = np.array(bdp_and_ppda["build_up_disruption"])
y = np.array(bdp_and_ppda["ppda"])
par = np.polyfit(x, y, 1, full=True)
slope = par[0][0]
intercept = par[0][1]
y_predicted = [slope * i + intercept for i in x]

r1 = p.circle(x="build_up_disruption", y="ppda", size=8, source=source, color="color")
width = 1
height = 1.0
image3 = ImageURL(url=dict(value=url), x=-2, y=8, h=height, w=width, anchor="bottom_left")
p.add_glyph(source, image3)
for _, row in bdp_and_ppda.iterrows():
    url = f"https://media.api-sports.io/football/teams/{row['team_id']}.png"
    image3 = ImageURL(url=dict(value=url), y=row['ppda'], x=row['build_up_disruption'], anchor="center")
    p.add_glyph(source, image3)

p.xaxis.axis_label = "Build-up disruption"
p.yaxis.axis_label = "PPDA"
p.line(x, y_predicted, color="black")
hover = HoverTool(renderers=[r1], tooltips=TOOLTIPS)
p.add_tools(hover)

script, div = components(p)
items = bdp_and_ppda.to_dict("records")

fileLoader = FileSystemLoader("reports")
env = Environment(loader=fileLoader)

rendered = env.get_template("tilt_and_bdp_vs_ppda.html").render(
    script=script,
    div=div,
    items = items,
)
print(rendered)
