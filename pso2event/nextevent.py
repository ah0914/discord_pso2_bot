import datetime
class nextevent:
    def nextevent():
        global date 
        date = datetime.datetime.now()
        #30分より前ならHH:30から検索開始
        if date.minute <= 30:
            now = date.strftime('%m/%d%H:30')

        #30分以降ならHH+1:00から検索
        else:
            date += datetime.timedelta(hours=1)
            now = date.strftime('%m/%d%H:00')

        with open('boost.txt') as f:
            lines = f.readlines()

        for i in range(1,48):
            txt = ([s for s in lines if s.startswith(now)])
            if len(txt)!=0:
                a = txt
                ne = now[:5]
                break
            now = datetime.datetime.strptime(now,'%m/%d%H:%M')
            now += datetime.timedelta(minutes=30)
            now = now.strftime('%m/%d%H:%M')

        x = (a[0].replace(ne,''))
        return x

    def nowtime():
        d = date.strftime('%m/%d %H:%M')
        return d
