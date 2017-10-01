import pandas
from pandas import DataFrame
import os
import json
import requests
from src.helpers.definitions import se_dir
from time import sleep

stupidly_publicly_available_api_key_lol = 'd805e84363494ca03b9b52d5a505c4d1'
trip_lengths_map_file = 'trip_lengths_map.json'


def find_trip_length(orig, dest):
  url = 'https://airport.api.aero/airport/distance/{}/{}'.format(orig, dest)
  r = requests.get(url, params={'user_key': stupidly_publicly_available_api_key_lol})
  resp_data = json.loads(r.text.lstrip('callback(').rstrip(')'))

  if not resp_data.get('success'):
    print(resp_data.get('errorMessage'))
    return None

  distance = resp_data.get('distance')

  if distance is None:
    return None

  return float(distance.replace(',', ''))


def get_trip_lengths_map():
  if not os.path.exists(trip_lengths_map_file):
    return {}

  with open('trip_lengths_map.json') as f:
    return json.load(f)


if __name__ == '__main__':
  data = pandas.read_csv('{}/h_satellite_ticket.csv'.format(se_dir), sep=',')
  headers = list(data)
  origins = data.values[:, headers.index('board_point')]
  destinations = data.values[:, headers.index('off_point')]
  uuids = data.values[:, headers.index('emcg_uuid')]
  num_flights = len(origins)

  print('Calculating distances for {} flights...'.format(num_flights))

  trip_lengths_map = get_trip_lengths_map()
  uuid_map = {}
  i = 0

  try:
    for orig in origins:
      if i % 10 == 0 and i > 0:
        print('Done with {}/{}'.format(i, num_flights))

      uuid = uuids[i]
      dest = destinations[i]
      trip_key = '{}|{}'.format(orig, dest)
      reverse_trip_key = '{}|{}'.format(dest, orig)

      if trip_key in trip_lengths_map:
        trip_length = trip_lengths_map[trip_key]
      elif reverse_trip_key in trip_lengths_map:
        trip_length = trip_lengths_map[reverse_trip_key]
      else:
        try:
          trip_length = find_trip_length(orig, dest)
        except BaseException:
          i += 1
          continue

        if not trip_length:
          print('Distance not found between {} and {}'.format(orig, dest))
          i += 1
          continue

        trip_lengths_map[trip_key] = trip_length

      uuid_map[uuid] = trip_length

      i += 1
      sleep(1)  # Don't get kicked off API
  except KeyboardInterrupt:
    print('Bye Bye')

  print('Found {} distances for {} flights.'.format(len(uuid_map), num_flights))

  with open('trip_lengths.json', 'w+') as f:
    f.write(json.dumps(uuid_map, indent=2))

  df = DataFrame.from_dict({
    'emcg_uuid': list(uuid_map.keys()),
    'flight_distance': list(uuid_map.values())
  })

  df.to_csv('{}/flight_distances.csv'.format(se_dir), index=False)

  with open(trip_lengths_map_file, 'w+') as f:
    f.write(json.dumps(trip_lengths_map, indent=2))