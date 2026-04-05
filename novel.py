import requests as me
import bs4 as i
import re
from urllib.parse import urlparse

# TODO 只需求改URL
url = "https://www.biquge.tw/book/1/1.html"
header = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/138.0.0.0 Safari/537.36",
    "Cookie": "_ga=GA1.1.513633547.1774977737; _im_vid=01KN6SN934WXAXEJ78MDS3CY6X; "
              "oid=%257B%2522oid%2522%253A%25227d368d35-2e79-11f1-9d22-42010a00004b%2522%252C%2522ts%2522%253A"
              "-62135596800%252C%2522v%2522%253A%252220201117%2522%257D; "
              "_ga_6FXZK5TW8D=GS2.1.s1775159485$o3$g1$t1775159498$j47$l0$h0; "
              "cf_clearance=owGmC7fBRQ7RR3f75zdiNX.48QTZ583g0rmmieLcXlc-1775161096-1.2.1.1"
              "-nf6Ow9iUFzvFESD7jVWxmsBwWXV7yyEZw1ZebyxzN6gwfSS8NEcEnzET_XqAJmhguDGcIgedPQUdHMkgvpGqdm.rIZuk"
              ".xVWfKvveku6ouVhtq7HarKcBnWQzImyhwnduAxkG6orNcI"
              ".HVeG8YM3nfnKgAtgeI57BTIOG8qZPtyO99BJwnTSpDLyjx5REeGf9Ljyq7e5yngm3O68IYHN9SfuI0wFxb2sbDrzfIl4Go0 "
}
host = ""


def writeFile(index, name, data):
    print(f"novel/out/{index:03}{name}")
    with open(f"novel/out/{index:03}.html", 'w') as file:
        file.write('<?xml version="1.0" encoding="utf-8"?>')
        file.write('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"')
        file.write('"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">')
        file.write('<html xmlns="http://www.w3.org/1999/xhtml">')
        file.write('<head><title>')
        file.write(f'{name}')
        file.write('</title></head><body>')
        file.write(f"<h1>{index:03 }{name}</h1>")
        file.write(data)
        file.write('</body></html>')


def haveNextPage(page):
    nextNmae = page.find("a", rel="next").text
    if nextNmae.__eq__("下一页"):
        return True
    else:
        return False


def nextPageLink(page):
    aLable = page.find('a', string='下一页')
    if aLable:
        pass
    else:
        aLable = page.find('a', string='下一章')
    if aLable and 'href' in aLable.attrs:
        return aLable['href']
    else:
        print('没有找到下一页链接')


def getBookName(reponse):
    root = i.BeautifulSoup(reponse.text, "html.parser")
    bookread = root.find("div", class_="book read")
    name = bookread.find("h1").text.strip()
    name = re.sub(r'\s*【\d{3}】\s*', '', name)
    name = re.sub(r'\（\s*\d+\s*/\s*\d+\s*\）', '', name)
    return name.strip()


def getContextAndPage(reponse):
    root = i.BeautifulSoup(reponse.text, "html.parser")
    context = root.find("div", class_="read-content")
    page = root.find("div", class_="read-page")
    result = re.sub(r'<div\s+[^>]*>', '', str(context))
    result = re.sub(r'</div>', '', result)
    return result.strip(), page


def pa(url):
    if url.startswith("https", 0, 5):
        pass
    else:
        url = host + url
    print(url)
    reponse = me.get(url, headers=header, timeout=(1, 2))
    result, page = getContextAndPage(reponse)
    url = nextPageLink(page)
    if haveNextPage(page):
        t1, url, abandon = pa(url)
        result += t1
    return result, url, getBookName(reponse)


# TODO 如果你想从中间某章节开始下载，则应修改start参数为对应章节数，避免下载结果的顺序发生错乱
# TODO 如果你想下载中间某部分章节而不是想下载整本书，则应该修改end参数为结束章节数；同时修改select为2
def run(url, start=1, end=1, select=1):
    try:
        while True and select == 1 or start <= end and select == 2:
            result, url, name = pa(url)
            writeFile(start, name, result)
            if len(url) < 20:
                break
            start += 1
    except BaseException:
        print("错误重试")
        run(url, start, end)


if __name__ == '__main__':
    urlObj = urlparse(url)
    host = f"{urlObj.scheme}://{urlObj.hostname}"
    run(url)
