import os
import datetime
import re
import csv
import Adafruit_DHT

STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static') 
DATA_PATH = os.path.join(STATIC_DIR, 'data.csv')

def read_DS18B20():
  path = '/sys/bus/w1/devices/28-0517c47426ff/w1_slave'
  with open(path, 'r') as instrm:
    content = instrm.read()
  match = re.search('t=(\d+)', content)
  return int(match.group(1))/1000.0 if match else None

def read_DHT11():
  return Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, 17)

def capture_photo(path):
  os.system('raspistill -f -q 10 -vf -o %s -ev +5 --brightness 55' % path)

def find_last_file(folder, suffix):
  last_timestamp, last_path = None, None
  for relpath in os.listdir(folder):
    if not relpath.endswith(suffix):
      continue
    path = os.path.join(folder, relpath)
    timestamp = os.path.getmtime(path)
    if not last_timestamp or last_timestamp < timestamp:
      last_timestamp, last_path = timestamp, path
  return last_path

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

def add_to_data(time_str, w_temp):
  fields, data = read_data()
  new_fields = [f for f in ['time', 'w_temp'] if f not in fields]
  fields.extend(new_fields)
  with open(DATA_PATH, 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fields)
    writer.writeheader()
    for d in data:
      writer.writerow(d)
    writer.writerow({'time': time_str, 'w_temp': w_temp})

def photo_relpath(time_str):
  return 'photo_%s.jpg' % time_str

def datetime_to_str(dt):
  return '%04d_%02d_%02d_%02d_%02d_%02d' % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second) 

def str_to_datetime(time_str):
  return datetime.datetime(*[int(tok) for tok in time_str.split('_')])

def run():
  dt = datetime.datetime.now()
  time_str = datetime_to_str(dt)
  # photo_path = os.path.join(STATIC_DIR, photo_relpath(time_str))
  # capture_photo(photo_path)
  w_temp = read_DS18B20()
  # humid, r_temp = read_DHT11()
  add_to_data(time_str, w_temp)

if __name__ == '__main__':
  run()
