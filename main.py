import requests
import nex
# from imp import reload
import time

url = 'http://119.28.212.154:8080/nex.py'
versionurl = 'http://119.28.212.154:8080/' + str(nex.version)


def update():
    nex.run()
    # r = requests.get(url=versionurl)
    # if r.__bool__():
    #     print('当前已是最新版本，无需更新！')
    #     try:
    #         nex.run()
    #     except Exception as e:
    #         print(e)
    #         time.sleep(3)
    #         nex.run()
    # else:
    #     print('程序更新中，请稍后....')
    #     r = requests.get(url=url)
    #     with open("nex.py", "wb") as code:
    #         code.write(r.content)
    #     print('更新完成！')
    #     reload(nex)
    #     try:
    #         nex.run()
    #     except Exception as e:
    #         print(e)
    #         time.sleep(3)
    #         nex.run()

if __name__ == '__main__':
    nex.run()
    # if nex.check():
    #     print('检查更新....')
    #     try:
    #         update()
    #     except:
    #         print('检查更新失败，下次重试...')
    #         try:
    #             nex.run()
    #         except Exception as e:
    #             print(e)
    #             time.sleep(3)
    #            nex.run()

