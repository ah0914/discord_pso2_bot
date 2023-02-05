import requests
from bs4 import BeautifulSoup
import csv
import os
class eventgetter:
    def getcsv():
#スクレイピングしてcsvに書き出し 
        r = requests.get('http://pso2.jp/players/boost/')
        soup = BeautifulSoup(r.text, 'html.parser')

        table = soup.find(class_='eventTable--event')
        rows = table.findAll('tr')

        with open("boost.csv", "w", encoding='utf-8') as file:
            writer = csv.writer(file)
            for row in rows:
                csvRow = []
                for cell in row.findAll(['td','th']):
                    csvRow.append(cell.get_text())
                writer.writerow(csvRow)

#txtに整形してcsvを削除
        txt = list()

        with open('boost.csv') as f:
            f_in = [s for s in f if '緊急' in s]

        os.remove('boost.csv')

        for l in f_in:
            txt.append(l.split('緊急')[1])

        txt.sort()

        with open('boost.txt', 'w') as f:
            for l in txt:
                print(l,end='', file=f)

