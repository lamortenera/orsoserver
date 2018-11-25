import os
import datetime
import re
import csv
from ruuvitag_sensor.ruuvi import RuuviTagSensor

STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
DATA_PATH = os.path.join(STATIC_DIR, 'data.csv')
TAGS = {
  "FB:B7:8B:F3:32:53": "A: Camera da letto",
  "F0:C9:25:26:3B:12": "B: Balcone",
  "FC:52:08:88:81:E1": "C: Salotto"
}

COL_TAG_NAME = "tag_name"
COL_TEMP = "temp"
COL_HUMIDITY = "humidity"
COL_TIME = "time"

def read_tags():
  raw_tag_datas = RuuviTagSensor.get_data_for_sensors(TAGS.keys(), 5)
  tag_datas = []
  for mac, raw_tag_data in raw_tag_datas.items():
    tag_name = TAGS.get(mac)
    if not tag_name:
      continue
    tag_datas.append({
        COL_TAG_NAME: tag_name,
        COL_TEMP: raw_tag_data.get("temperature"),
        COL_HUMIDITY: raw_tag_data.get("humidity")})
  return tag_datas

def read_data():
  try:
    with open(DATA_PATH) as csvfile:
      reader = csv.DictReader(csvfile)
      data = list(reader)
      if data:
        return reader.fieldnames, data
  except:
    pass
  return [], []

def add_to_data(rows):
  fields, data = read_data()
  for d in rows:
    for key in d.keys():
      if key not in fields:
        fields.append(key)
  with open(DATA_PATH, 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fields)
    writer.writeheader()
    for d in data:
      writer.writerow(d)
    for d in rows:
      writer.writerow(d)

def datetime_to_str(dt):
  return '%04d_%02d_%02d_%02d_%02d_%02d' % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)

def str_to_datetime(time_str):
  return datetime.datetime(*[int(tok) for tok in time_str.split('_')])

def run():
  dt = datetime.datetime.now()
  time_str = datetime_to_str(dt)
  tag_datas = read_tags()
  for data in tag_datas:
    data[COL_TIME] = time_str
  add_to_data(tag_datas)

if __name__ == '__main__':
  run()
