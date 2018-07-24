import hashlib
import hmac
from config import *
import time
import requests
import json
import threading
import sys
import os
import wmi
import sqlite3
import pymysql
import config
from api import *
version = 'nex1.0'

def getHardDiskNumber():
    c = wmi.WMI()
    for physical_disk in c.Win32_DiskDrive():
        return physical_disk.SerialNumber

def insert(code,pcnumber):
    conn = pymysql.connect(host="cdb-73w89woy.bj.tencentcdb.com", user="root", passwd="niba1234", db="ocx", port=10001)
    c = conn.cursor()
    params = (code,pcnumber)
    try:
        c.execute('INSERT INTO book VALUES (%s,%s)', params)
    except Exception as e:
        print(e)

    conn.commit()
    conn.close()
def delete(id):
    conn = pymysql.connect(host="cdb-73w89woy.bj.tencentcdb.com", user="root", passwd="niba1234", db="ocx", port=10001)
    c = conn.cursor()
    t = (id,)
    c.execute('DELETE FROM book WHERE code=%s', t)
    conn.commit()
    conn.close()
def validate(code):
    try:
        code1 = code[0:7]
        code2 = code[7:11]
        code2 = int(code2)+24
        code = code1 + str(code2)
        # print(code)
        pnumber = str(getHardDiskNumber())
        # print(pnumber)
        conn = pymysql.connect(host="cdb-73w89woy.bj.tencentcdb.com", user="root", passwd="niba1234", db="ocx", port=10001)
        c = conn.cursor()
        t = (code,)
        c.execute('SELECT * FROM book WHERE code=%s', t)

        num = c.fetchone()[1]
        # print(num)
        if num == '0':
            delete(code)
            insert(code,pnumber)
            print('注册码绑定成功！')
            return True
        elif num == pnumber:
            print('认证成功！')
            return True
        else:
            print('认证失败！')
            return False
    except:
        print('注册码无效！')
        return False

access_key = api_key

symbol = coin[0] + coin[1]
x = coin[0]
y = coin[1]

def sign(x):

    x = x.encode('utf-8')
    signature = hashlib.md5(x)
    return signature.hexdigest()


def getdepth():
    tonce = int(time.time() * 1000)
    baseurl = 'https://api.coinex.com/v1/market/depth?'
    market_code = symbol
    canonical_query = 'access_id=' + access_key + '&market=' + market_code + '&merge=0.00000001&tonce=' + str(tonce)
    url = baseurl + canonical_query
    req = requests.request(method='GET',url=url)
    # print(req.text)
    try:
        req = req.json()['data']
        ask = float(req['asks'][0][0])
        bid = float(req['bids'][0][0])
        askamount = float(req['asks'][0][1])
        bidamount = float(req['bids'][0][1])
        print('买一：',bid,'卖一',ask)
        return bid,ask,askamount,bidamount
    except Exception as e:
        if 'does not exist' in req.text:
            print(req.text)
            print('API错误，请检查config配置是否正确，或登录平台查看API是否健在~~')
        elif 'The tonce' in req.text:
            print('请调整电脑时间，与北京时间相差不超过5秒！')
        elif 'market_code' in req.text:
            print('交易对填写错误，交易货币在前，基础货币在后，全部小写')
        else:
            print(req.text)
            print(e)
            print('出现异常，如果看不懂请截图发给管理员！')
        time.sleep(5)
        restart()

def getbalance():
    tonce = int(time.time() * 1000)
    baseurl = 'https://api.coinex.com/v1/balance/?'
    canonical_query = 'access_id=' + access_key + '&tonce=' + str(tonce)

    payload = canonical_query + '&secret_key='+api_secret

    signature = sign(payload).upper()
    url = baseurl + canonical_query
    header = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
        'authorization': signature
    }
    req = requests.request(method='GET',headers=header, url=url)
    # print(req.text)
    try:
        data = req.json()['data']

        availablex = float(data[x.upper()]['available'])
        lockedx = float(data[x.upper()]['frozen'])
        balancex = float(availablex)+float(lockedx)

        availabley = float(data[y.upper()]['available'])
        lockedy = float(data[y.upper()]['frozen'])
        balancey = float(availabley) + float(lockedy)

        # print(availablex, balancex, availabley, balancey)
        return availablex,balancex,availabley,balancey,lockedx,lockedy
    except Exception as e:
        if 'does not exist' in req.text:
            print(req.text)
            print('API错误，请检查config配置是否正确，或登录平台查看API是否健在~~')
        elif 'The tonce' in req.text:
            print('请调整电脑时间，与北京时间相差不超过5秒！')
        elif 'market_code' in req.text:
            print('交易对填写错误，交易货币在前，基础货币在后，全部小写')
        else:
            print(req.text)
            print(e)
            print('出现异常，如果看不懂请截图发给管理员！')
        time.sleep(5)
        restart()
def buy_action(symbol,price,amount,time):
    request_client = RequestClient()
    data = {
        "amount": amount,
        "price": price,
        "type": "buy",
        "market": symbol
    }

    response = request_client.request(
        'POST',
        '{url}/v1/order/limit'.format(url=request_client.url),
        json=data,
    )

    try:
        req = json.loads(response.data)
    except:
        print(req)
    try:
        print('买单下单成功 价格：', price, '数量：', amount, '订单ID：', req['data']['id'])
    except:
        print('买单异常：', req['message'])

def sell_action(symbol,price,amount,time):
    request_client = RequestClient()
    data = {
            "amount": amount,
            "price": price,
            "type": "sell",
            "market": symbol
        }

    response = request_client.request(
            'POST',
            '{url}/v1/order/limit'.format(url=request_client.url),
            json=data,
    )

    try:
        req = json.loads(response.data)
    except:
        print(req)
    try:
        print('卖单下单成功 价格：',price,'数量：',amount,'订单ID：',req['data']['id'])
    except:
        print('卖单异常：',req['message'])


def cancelorders():
    request_client = RequestClient()
    params = {
        'market': symbol
    }
    req = request_client.request(
        'GET',
        '{url}/v1/order/pending'.format(url=request_client.url),
        params=params
    )
    req = json.loads(req.data)
    orders = req['data']['data']
    if len(orders) > 0:
        for li in orders:
            cancel_order(li['id'],symbol)
def balancecheck():
    print('余额动平衡....')
    aa = getbalance()
    balancex = aa[0]
    balancey = aa[2]
    price = getdepth()
    askamount = price[2]
    bidamount = price[3]
    balancey2x = balancey / price[1]
    tonce = int(time.time() * 1000)
    if balancex < balancey2x*0.9:
        buy_action(symbol,price[1],min(round(balancey2x*0.2,4),askamount*0.7),tonce)
    elif balancey2x < balancex*0.9:
        sell_action(symbol,price[0],min(round(balancex*0.2,4),bidamount*0.7),tonce)
def go():
    global amount1, baseprice, f
    aa = getbalance()
    time.sleep(0.5)
    balancex = aa[0]
    balancey = aa[2]
    frozx = aa[4]
    frozy = aa[5]
    price = getdepth()
    bidamount = price[2]
    askamount = price[3]
    balancey2x = balancey / price[0]
    ss = aa[1] * price[0] + aa[3]
    print('账户余额：%s: 可用：%s 冻结：%s | %s: 可用：%s 冻结： %s (%s) 》》》折合总资产： %s %s 当前版本：V%s' % (
    x, balancex, frozx, y, balancey, frozy, num, ss, y, version))
    if amount1 == 0 and (f == 0 or baseprice == 0):
        print('当前模式：仓位下单 & 无波动安全区间  当前版本：', version)
    elif amount1 == 0 and f != 0:
        print('当前模式：仓位下单 & 安全区间(', f, '%', ')', '当前版本：', version)
    elif amount1 != 0 and (f == 0 or baseprice == 0):
        print('当前模式：固定下单数量（%s）& 无波动安全区间 当前版本：%s' % (amount1, version))
    else:
        print('当前模式：固定下单数量（', amount1, ')', ' & ', '安全区间(', f, '%', ')', '当前版本：', version)

    if amount1 != 0:
        amount = amount1
    else:
        amount = round((min(balancex, balancey2x)) * per_amount, 4)

    price1 = round((price[0] + price[1]) / 2, price_decimal_digits)
    if baseprice != 0 and f != 0:

        aa = abs((price[1] - baseprice) / baseprice)
        bb = abs((baseprice - price[0]) / baseprice)
        ff = round(max(aa, bb), 8)
        if ff > (f / 100):
            print('当前价格波动： %s 超出预设安全波动区间，暂停刷单' % ff)
            time.sleep(5)
        else:
            print('当前价格波动：%s' % ff)
            price2 = price1
            amount2 = amount
            symbol2 = symbol
            if price1 > price[0] and price1 < price[1]:
                if balancex > amount2 and balancey > price1 * amount:
                    t1 = threading.Thread(target=buy_action, args=(symbol, price1, amount))
                    t2 = threading.Thread(target=sell_action, args=(symbol2, price2, amount2))
                    t1.start()
                    t2.start()
                    t1.join()
                    t2.join()
                    print('**************************************************************************')

                else:
                    print('余额不足...')
                    # balancecheck()
                    print('**************************************************************************')
            elif price1 != 0 and kissmyass == 1:
                print('吃单模式')
                amount1 = round(min(bidamount, askamount) * 0.6, 4)
                amount2 = round((min(balancex, balancey2x)) * per_amount, 4)
                amount = min(amount1, amount2)
                amount2 = amount
                tonce = int(time.time() * 1000)
                t1 = threading.Thread(target=buy_action, args=(symbol, price[1], amount, tonce))
                t2 = threading.Thread(target=sell_action, args=(symbol2, price[0], amount2, tonce))
                t1.start()
                t2.start()
                t1.join()
                t2.join()
                print('**************************************************************************')
            else:

                print('盘口价格差过低，放弃下单')
                print('**************************************************************************')
    else:
        price2 = price1
        amount2 = amount
        symbol2 = symbol
        if price1 > price[0] and price1 < price[1]:
            if balancex > amount2 and balancey > price1 * amount:
                # print('本次下单数量：', amount)
                tonce = int(time.time() * 1000)
                t1 = threading.Thread(target=buy_action, args=(symbol, price1, amount, tonce))
                t2 = threading.Thread(target=sell_action, args=(symbol2, price2, amount2, tonce))
                t1.start()
                t2.start()
                t1.join()
                t2.join()
                print('**************************************************************************')

            else:
                print('余额不足...')
                # balancecheck()
                print('**************************************************************************')
        elif price1 != 0 and kissmyass == 1:
            print('吃单模式')
            amount1 = round(min(bidamount, askamount) * 0.6, 4)
            amount2 = round((min(balancex, balancey2x)) * per_amount, 4)
            amount = min(amount1, amount2)
            amount2 = amount
            tonce = int(time.time() * 1000)
            t1 = threading.Thread(target=buy_action, args=(symbol, price[1], amount))
            t2 = threading.Thread(target=sell_action, args=(symbol2, price[0], amount2))
            t1.start()
            t2.start()
            t1.join()
            t2.join()
            print('**************************************************************************')
        else:

            print('盘口价格差过低，放弃下单')
            print('**************************************************************************')
def restart():
    python = sys.executable
    os.execl(python, python, *sys.argv)
def ini():
    global amount1,baseprice,f1
    try:
        baseprice = config.baseprice
        f1 = config.f

    except:
        with open("config.py", "a",encoding='UTF-8') as f:
            f.write('\n')
            f.write('#baseprice为安全波动范围的基准价，f为波动幅度（1-10之间取值，代表上线波动几个点，大于这个范围停止刷单）' + '\n')
            f.write('baseprice = 0' + '\n')
            f.write('f = 0' + '\n')
        baseprice = 0
        f1 = 0
    try:
        amount1 = config.amount1
    except:
        with open("config.py", "a", encoding='UTF-8') as f:
            f.write('\n')
            f.write('#amount1为固定下单数量（交易对前面那个币的数量），如果设置固定下单，那百分比下单则无效' + '\n')
            f.write('amount1 = 0' + '\n')
        amount1 = 0
def run():
    # print('')
    # print('')
    # print('大家不要着急嘛，等稳定了咱们再刷可好？')
    # print('')
    #
    # print('*****************************************************************')
    # print('*                           ')
    # print('*     本次更新：             ')
    # print('* 1.刷单安全波动区间范围设置')
    # print('* 2.可选固定下单数量设置     ')
    # print('* 以上功能默认关闭，如需开启，请查看config说明进行配置')
    # print('* 5秒后开始刷单....')
    # print('*****************************************************************')
    # time.sleep(5)
    try:
        ini()
        # balancecheck()
        global num,liao
        liao = 0
        num = 0
        while True:
            # go()
            try:
                go()
            except Exception as e:
                # print(e)
                time.sleep(2.5)
                run()
            time.sleep(1)
            num = num + 1
            if num%10 == 0:
                try:
                    print('挂单检测....')
                    cancelorders()
                    time.sleep(2)
                    balancecheck()
                except:
                    time.sleep(1)
    except:
        time.sleep(2)
        restart()


def check():

    if validationcode:
        if validate(validationcode):
            return True
    else:
        print('请填写注册码！')
        return False
if __name__ == '__main__':
    # tonce = int(time.time() * 1000)
    # cancelorders()
    # sell_action(symbol,0.0012559 ,50,tonce)
    # getbalance()
    run()
    # go()
    # getdepth()
    # balancecheck()


