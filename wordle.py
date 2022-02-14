import csv
import datetime
import os


def get_daily():
    now = datetime.datetime.now()
    month, day, year = now.strftime("%b"), str(now.day), str(now.year)

    with open(os.path.join('resources', 'wordle_key.csv'), newline='') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if (row[0], row[1], row[2]) == (month, day, year):
                return row[5]