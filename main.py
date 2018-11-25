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

def plot_data(data):
  data = pd.DataFrame.from_records(data)
  data['x'] = [batch.str_to_datetime(s) for s in data.time]
  data['w_temp'] = np.array(data.w_temp.replace("", "0"), dtype=float)
  data['r_temp'] = np.array(data.r_temp.replace("", "0"), dtype=float)
  data['humid'] = np.array(data.humid.replace("", "0"), dtype=float)
  fig, ax1 = plt.subplots()
  p1 = ax1.plot(data.x, data.w_temp, 'b', label='Temperatura sensore accurato')
  # p2 = ax1.plot(data.x, data.r_temp, 'g', label='Temperatura sensore scadente')
  ax1.set_xlabel('Tempo')
  plt.xticks(rotation='vertical')
  ax1.set_ylabel('Temperatura (C)')
  #ax2 = ax1.twinx()
  #p3 = ax2.plot(data.x, data.humid, 'r', label='Umidità')
  #ax2.set_ylabel('Umidità (%)')
  #lns = p1 + p2 + p3
  #ax1.legend(lns, [l.get_label() for l in lns]) 
  plt.title('Sensori')
  plt.gcf().autofmt_xdate()
  figfile = BytesIO()
  plt.savefig(figfile, format='png')
  return base64.b64encode(figfile.getvalue()).decode('ascii')


@app.route('/')
def index():
  _, data = batch.read_data()
  img_path = None
  chart_data = None
  time_str = None
  if data:
    last_time = data[-1]['time']
    last_temp = data[-1]['w_temp']
    # photo_relpath = batch.photo_relpath(last_time)
    # img_path = flask.url_for('static', filename=photo_relpath)
    chart_data = plot_data(data)
    time_str = str(batch.str_to_datetime(last_time)) + ", Temperatura: {} C".format(last_temp)
  return flask.render_template('index.html', 
          # img_path=img_path,
          chart_data=chart_data,
          time_str=time_str)

#@app.route('/timelapse')
#def timelapse():
#  _, data = batch.read_data()
#  if data:
#    for i, d in enumerate(data):
#      d['progress'] = '%d/%d' % (i + 1, len(data))
#      d['imgsrc'] = flask.url_for('static', filename=batch.photo_relpath(d['time']))
#      d['caption'] = str(batch.str_to_datetime(d['time']))
#  return flask.render_template('timelapse.html', data=data)

if __name__ == '__main__':
  app.run(debug=True, port=80, host='0.0.0.0')

