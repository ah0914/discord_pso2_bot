import datetime
def todayevent()
    a = ''
    date = datetime.datetime.now()
    nd = date.strftime('%m/%d')
    with open('boost.txt') as f:
        f_in = [s for s in f if nd in s]
    x = (nd+'の予告緊急は以下の通りです。')
    for l in f_in:
        l = l.replace(nd,'')
        a += l

    if a == '':
        x = ('本日の予告緊急はありません。')
