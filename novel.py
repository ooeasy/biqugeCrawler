import traceback

import requests as me
import bs4 as i
import re


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
        file.write(f"<h1>{name}</h1>")
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


def di(header, host, page):
    print(host + nextPageLink(page))
    reponse = me.get(host + nextPageLink(page), headers=header, timeout=(3, 5))
    result, page = getContextAndPage(reponse)
    if haveNextPage(page):
        result += di(header, host, page)
    return result


def pa(bookid, index, offset, header, host, router):
    offset -= 1
    url = host + router + f"/{bookid}/" + str(index + offset) + ".html"
    print(url)
    reponse = me.get(url, headers=header, timeout=(3, 5))
    print(reponse.status_code)
    result, page = getContextAndPage(reponse)
    if haveNextPage(page):
        result += di(header, host, page)
    return getBookName(reponse), result


def run(bookid, index, offset, header, host, router):
    temp = offset
    # TODO 在这里输入需要下载到第end章，目前版本需要在网页中查看目录确定总章数。请务必输入正确的参数，如果end数值小于实际章数，会导致下载不完整；如果end
    #  数值大于实际参数，会导致程序下载完后不断进行失败尝试死循环，此时使用Control+C中断程序不会影响已保存的结果
    end = 1
    try:
        for i in range(offset, end + 1):
            name, result = pa(bookid, index, i, header, host, router)
            writeFile(i, name, result)
            temp += 1
    except BaseException:
        print("错误重试")
        traceback.print_exc()
        # run(bookid, index, temp, header, host, router)


if __name__ == '__main__':
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
    host = "https://biquge.tw"
    router = "/book"
    # TODO 通过URL获取到这两个参数，详细过程参照README.md
    bookid = 9002
    index = 286409
    # 默认从第一章开始下载，如果你想要下载某些章节，请求改此参数为起始章节
    offset = 1
    run(bookid, index, offset, header, host, router)
