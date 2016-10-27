import csv
from datetime import datetime
import sys

import scratchdb

CSV_FILENAME = 'test-data/zip_codes_all_states.csv'

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python loadtest.py <path to csv file>')
    path = sys.argv[1]
    dbname = path.partition('/')[2].partition('.')[0]
    db = scratchdb.ScratchDB(dbname)
    with open(path) as f:
        csv_rows = csv.reader(f)
        header_row = next(csv_rows)
        print('header row is:')
        print(header_row)
        t_s = datetime.now()
        for i, (z, lat, lon, city, state, county) in enumerate(csv_rows):
            if i % 1000 == 0:
                print('Processing rows:', i, '-', i + 1000, 'time ellapsed:', datetime.now() - t_s)
            db.set(z, {'latitude': lat, 'longitude': lon, 'city': city, 'state': state, 'county': county})
    db.close()

