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
from io import BytesIO

app = flask.Flask(__name__)

def plot_col(df, col, title):
  y = np.array(df[col].replace("", None), dtype=float)
  labels = sorted(df[batch.COL_TAG_NAME].unique())
  for label in labels:
    rows = df[batch.COL_TAG_NAME] == label
    sub_x = df.x[rows]
    sub_y = y[rows]
    plt.plot(sub_x, sub_y, label=label)
  plt.title(title)
  plt.legend()
  figfile = BytesIO()
  plt.gcf().autofmt_xdate()
  plt.savefig(figfile, format='png')
  plt.clf()
  return base64.b64encode(figfile.getvalue()).decode('ascii')


@app.route('/')
def index():
  _, data = batch.read_data()
  time_str = None
  temp_chart = None
  humid_chart = None
  if data:
    df = pd.DataFrame.from_records(data)
    df['x'] = [batch.str_to_datetime(s) for s in df[batch.COL_TIME]]
    last_time = df.x.iloc[-1]
    temp_chart = plot_col(df, batch.COL_TEMP, 'temperatura')
    humid_chart = plot_col(df, batch.COL_HUMIDITY, 'umidità')
  return flask.render_template('index.html',
                               time_str=last_time,
                               temp_chart=temp_chart,
                               humid_chart=humid_chart)

if __name__ == '__main__':
  app.run(debug=True, port=80, host='0.0.0.0')

