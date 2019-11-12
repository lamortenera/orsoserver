import os
import flask
import batch
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime
import base64
import random
import json
from io import BytesIO

app = flask.Flask(__name__, static_folder=batch.STATIC_DIR)
_PLOTLY_COLORS = [
  '#1f77b4',
  '#ff7f0e',
  '#2ca02c',
  '#d62728',
  '#9467bd',
  '#8c564b',
  '#e377c2',
  '#7f7f7f',
  '#bcbd22',
  '#17becf'
]

def to_json(df, col, title, chart_id):
  y = np.array(df[col].replace("", None), dtype=float)
  labels = sorted(df[batch.COL_TAG_NAME].unique())
  data = []
  for label in labels:
    rows = df[batch.COL_TAG_NAME] == label
    sub_x = [str(dt) for dt in df.datetime[rows]]
    sub_y = y[rows]
    data.append({'x': list(sub_x), 'y': list(sub_y), 'mode': 'lines', 'name':
                 label})
  return {'id': chart_id, 'data': data, 'layout': {'title': title}}

def combine_plots(plot1, plot2, title, chart_id):
  data = []
  ytitle1 = plot1['layout']['title']
  legends = {}

  def config_legend(trace):
    name = trace['name']
    trace['legendgroup'] = name
    if name in legends:
      trace['showlegend'] = False
    else:
      legends[name] = _PLOTLY_COLORS[len(legends) % len(_PLOTLY_COLORS)]
      trace['showlegend'] = True
    trace['line'] = {'color': legends[name]}

  for trace in plot1['data']:
    trace['yaxis'] = 'y'
    config_legend(trace)
    data.append(trace)
  ytitle2 = plot2['layout']['title']
  for trace in plot2['data']:
    trace['yaxis'] = 'y2'
    config_legend(trace)
    data.append(trace)

  grid = {'row': 2, 'columns': 1, 'subplots': [['xy'], ['xy2']]}
  layout = {'title': title,
            'grid': grid,
            'yaxis': {'title': ytitle1, 'domain': [0.52, 1]},
            'yaxis2': {'title': ytitle2, 'domain': [0, 0.47]}}
  return {'id': chart_id, 'data': data, 'layout': layout}

@app.route('/')
def index():
  _, data = batch.read_data()
  time_str = None
  carts_json = None
  video = flask.url_for('static', filename='video.mp4')
  if data:
    df = batch.read_dataframe()
    last_time = df.datetime.iloc[-1]
    last_time_str = df.time.iloc[-1]
    temp_json = to_json(df, batch.COL_TEMP, 'temperatura', 'temp')
    humid_json = to_json(df, batch.COL_HUMIDITY, 'umidità', 'humid')
    sensors_json = combine_plots(temp_json, humid_json, 'sensori', 'sensors')
    charts_json = json.dumps([sensors_json])
  return flask.render_template('index.html',
                               nocache=random.random(),
                               last_time=last_time,
                               time_str=last_time_str,
                               charts_json=charts_json,
                               video=video)

if __name__ == '__main__':
  app.run(debug=True, port=80, host='0.0.0.0')

