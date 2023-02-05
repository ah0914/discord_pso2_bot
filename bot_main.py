import discord
import random
import cv2
import numpy as np
import re
import pandas as pd
import datetime
import shutil
import asyncio
import subprocess
import time
from misc import colors
from misc import gbftranslate
from pso2event import eventgetter, nextevent
from discord.ext import tasks

client = discord.Client()
channel_sent = None

#管理者の名前(終了処理等の呼び出し制限に使用)
admin_name = ''

#ここにtokenを入力
token = ''

#接続するチャンネルのID
channel_id = 0

#csv読み込み
df = pd.read_csv('memo.csv',index_col=0)
dr = pd.read_csv('reaction.csv',index_col=0)

@tasks.loop(seconds=60)
async def todays_event():
    #00:00に今日の緊急予定を表示する
    datecheck = datetime.datetime.now()
    date_nh = datecheck + datetime.timedelta(hours=1)
    datecheck_str = daycheck.strftime('%H:%M')
    if daycheck_str == '00:00':
        eventgetter.eventgetter.getcsv()
        a = ''
        date = datetime.datetime.now()
        nd = date.strftime('%m/%d')
        with open('boost.txt') as f:
            f_in = [s for s in f if nd in s]
        await channel_sent.send('日付が変わりました。\n今日の予告緊急は以下の通りです。')
        for l in f_in:
            l = l.replace(nd,'')
            a += l
        await channel_sent.send(a)

        x = nextevent.nextevent.nextevent()
        if date_nh.strftime('%H:%M') in str(x):
            await channel_sent.send('1時間後に'+ str(x) +'が発生します！')

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

    global channel_sent
    channel_sent = client.get_channel(channel_id)
    todays_event.start()

@client.event
async def on_message(message):

    #ボイスチャンネルに必要なグローバル変数の定義
    global vc
    vol = 0.025

    #bot判定
    if message.author.bot:
        return

    #記憶喪失になったときのために
    if message.content == ('!whoami'):
        await message.channel.send('君は' + message.author.name)
        return

    #ヘルプを表示
    if message.content == ('!help'):
        file_data = open('bothelp.txt', 'r')
        contents = file_data.read()
        await message.channel.send(contents)
        file_data.close()
        return

    #ダイスロール
    if re.fullmatch(r'!([0-9]+)d([0-9]+)', message.content):
        cmd = message.content.replace('!', '')
        x,y = cmd.split('d')

        #ダイスロールの内容に0が含まれていた場合のエラー処理
        if 0 in {int(x), int(y)}:
            await message.channel.send('ダイス振ってないじゃん')
            return

        #ダイスを振る回数を制限
        elif int(x) > 10000:
            await message.channel.send('えっ!?' + str(y) + '面ダイスを' + str(x) + '回も!?')
            return

        dice = 0
        for num in range(int(x)):
            dice += random.randint(1,int(y))

        a = message.author.name + 'さんの' + str(cmd) + 'の結果: ' + str(dice)
        await message.channel.send(a)
        return

    #メモ機能
    if message.content.startswith('!m'):
        cmd = message.content.replace('!m','')

        #メモを出力
        if cmd == ('o'):
            if message.author.name in df.index:
                out = (message.author.name + 'さんのメモ:\n' + df.at[message.author.name, 'txt'])
            else:
                out = (message.author.name + 'さんのメモはまだありません。')

        #メモに書き込み
        elif cmd.startswith('m '):
            memo = cmd.replace('m ','')
            df.at[message.author.name, 'txt'] = memo
            df.to_csv('memo.csv')
            out = (message.author.name + 'さんのメモ:\n' + memo + '\nを作成しました。')

        #メモに追記
        elif cmd.startswith('a '):
            memo = cmd.replace('a ','')
            df.at[message.author.name, 'txt'] += '\n' + memo
            df.to_csv('memo.csv')
            out = (message.author.name + 'さんのメモに\n' + memo + '\nと追記しました。')

        #メモを消去
        elif cmd == ("c"):
            df.at[message.author.name, 'txt'] = "まだメモがありません。"
            df.to_csv('memo.csv')
            out = (message.author.name + 'さんのメモを消去しました。')

        else:
            out = ('!mo,!mm,!ma,!mcでメモ機能を利用できます。')

        await message.channel.send(out)
        return

    #"〜が欲しい"でファイル送信
    if message.content.endswith('欲しい'):
        cmd = message.content

        #クワイン
        elif cmd.startswith('お前が'):
            shutil.make_archive('../ぼく', 'zip', root_dir='./')
            f = '../ぼく.zip'

        #リアクション一覧のCSVを吐き出す
        elif cmd.startswith('語彙力が'):
            f = 'reaction.csv'

        #保存されている曲を吐き出す
        elif cmd.startswith('曲が'):
            f = 'bgm.mp3'

        else:
            return

        await message.channel.send(file=discord.File(f))
        return

    #言葉とそれに対しての返答を覚えさせる
    if message.content.startswith('!learn '):
        cmd = message.content.replace('!learn ','')

        #コマンド構文エラー
        if not ', ' in cmd:
            await message.channel.send('すみません、よくわかりません。')
            return

        iw, ow = cmd.split(', ',1)

        #コマンドを覚えさせようとした場合
        if iw.startswith('!'):
            await message.channel.send('コマンドを覚えさせようとするんじゃない')
            return

        #「〜欲しい」を覚えさせようとした場合
        elif iw.endswith('欲しい'):
            await message.channel.send('～欲しいは覚えさせられません。')
            return

        dr.loc[iw] = ow
        dr.to_csv('reaction.csv')
        await message.channel.send('今度から「' + iw + '」って言われたら「' + ow + '」って返すよ！')
        return

    #人工無能
    if message.content in dr.index:
        await message.channel.send(dr.at[message.content,'reply'])
        return

    #終了処理
    if message.content == ('!exit'):
        if message.author.name == (admin_name):
            await message.channel.send('botを停止します。')
            await client.logout()
            await sys.exit()
            cleanup()

    #再起動
    if message.content == ('!reboot'):
        if message.author.name == (admin_name):
            await message.channel.send('再起動します')
            subprocess.call(['python3', 'rollbot.py'])
            await client.logout()
            await sys.exit()

    #ボイスチャンネル周り
    #音量
    if message.content.startswith('!vol '):
        cmd = message.content.replace('!vol ','')
        vol = float(cmd) / 1000
        vc.source.volume = float(vol)
        await message.channel.send('音量を'+cmd+'に設定しました。')

    #接続
    if message.content.startswith('!join'):
        vc = await discord.VoiceChannel.connect(message.author.voice.channel)

    #切断
    if message.content.startswith('!dc'):
        await vc.disconnect()

    #再生
    if message.content == ('!p'):
        if not vc.is_playing():
            vc.play(discord.FFmpegPCMAudio('bgm.mp3'))
            vc.source = discord.PCMVolumeTransformer(vc.source)
            vc.source.volume = vol

    #一時停止
    if message.content == ('!pause'):
        if vc.is_playing():
            vc.pause()

    #再開
    if message.content == ('!resume'):
        if vc.is_paused():
            vc.resume()

    #停止
    if message.content == ('!stop'):
        if vc.is_playing():
            vc.stop()
            discord.FFmpegPCMAudio = read()

    #曲をbgm.mp3としてダウンロード
    if message.content.startswith('!dl '):
        msg = message.content.replace('!dl ','')
        subprocess.call(['rm','bgm.mp3'])
        subprocess.call(['youtube-dl',msg,'-x','--audio-format','mp3','-o','bgm.mp3'])
        await message.channel.send('曲のダウンロードが完了しました。')

    #曲をダウンロードして再生
    if message.content.startswith('!p '):
        msg = message.content.replace('!p ','')
        subprocess.call(['rm','bgm.mp3'])
        subprocess.call(['youtube-dl',msg,'-x','--audio-format','mp3','-o','bgm.mp3'])
        if vc.is_playing():
            vc.stop()
        if not vc.is_playing():
            vc.play(discord.FFmpegPCMAudio('bgm.mp3'))
            vc.source = discord.PCMVolumeTransformer(vc.source)
            vc.source.volume = vol

    #曲をスキップ(次の曲がない場合は最初から再生)
    if message.content == ('!skip'):
        if vc.is_playing():
            vc.stop()
            vc.play(discord.FFmpegPCMAudio('bgm.mp3'))
            vc.source = discord.PCMVolumeTransformer(vc.source)
            vc.source.volume = vol

    #音割れポッター
    if message.content == ('?????'):
        vc = await discord.VoiceChannel.connect(message.author.voice.channel)
        vc.play(discord.FFmpegPCMAudio('oto.mp3'))
        time.sleep(8)
        await vc.disconnect()

    #予告表をとってくる
    if message.content == ('!ge'):
        eventgetter.eventgetter.getcsv()
        await message.channel.send('予告緊急リストを更新しました。')

    #今日の緊急予定を表示
    if message.content == ('!te'):
        a = ''
        date = datetime.datetime.now()
        nd = date.strftime('%m/%d')
        with open('boost.txt') as f:
            f_in = [s for s in f if nd in s]
        await message.channel.send(nd+'の予告緊急は以下の通りです。')
        for l in f_in:
            l = l.replace(nd,'')
            a += l
        await message.channel.send(a)

    #次の緊急予定を表示
    if message.content == ('!ne'):
        try:
            x = nextevent.nextevent.nextevent()
            await message.channel.send('次の予告緊急は\n'+ str(x) +'です。')
        except:
            await message.channel.send('直近24時間以内に予定が無いか、予告緊急リストが最新のものではありません。\n!geでリストの再取得を試してみてください。')

    #ランダムでラッキーカラーを表示
    if message.content == ('!colors'):
        colors.pcolor()
        f = 'color.png'
        await message.channel.send('ラッキーカラーはこれ！')
        await message.channel.send(file=discord.File(f))

    #グラブル変換
    if message.content.startswith('!tr '):
        msg = message.content.replace('!tr ','')
        await message.channel.send(gbftranslate.gbt(msg))


client.run(token)
