__author__ = 'fabio.lana'

import csv
import os

os.remove('test.csv')

with open('test.csv', 'wb') as csvscrittura:
    scrittore = csv.writer(csvscrittura, delimiter=',')
    data = [['1', 0],
            ['2', 0],
            ['3', 0],
            ['4', 0],
            ['5', 0],
            ['6', 0],
            ['7', 0],
            ['8', 0],
            ['9', 0],
            ['10', 0],
            ['11', 0],
            ['12', 0]]

    scrittore.writerows(data)