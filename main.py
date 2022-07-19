
import requests
import re

BASE_DOMAIN = 'http://aqdygg.com'
# 1.将目标网站上的页面抓取下来

HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36"
}


def get_detail_url(url):
    response = requests.get(url, headers=HEADERS)
    # response.text
    # response.con tent
    # requests库，默认会使用自己猜测的编码方式将抓取的网页解码 抓取页面乱码
    text = response.content.decode(encoding='gbk', errors='ignore')
    contents_re = re.compile(r"<ul class=\".*?\" id=\"contents\">([\s\S]*?) </ul>", re.M)
    contents_text = contents_re.search(text).group(0)
    details_re = re.compile("href=\"(.*?)\">详细", re.M)
    details_list = details_re.findall(contents_text)
    return details_list


def parse_detail_page(path):
    movie = {}
    response = requests.get(BASE_DOMAIN + path, headers=HEADERS)
    text = response.content.decode(encoding='gbk', errors='ignore')
    # print(text)
    title = re.search("<h2>(.*?)</h2>", text).group(1)
    video_dict = {}
    p_list = re.findall("<p class=\"play-list\">([\s\S]*?)</p>", text, re.M)[1]
    a_list = re.finditer("<a *?title='(?P<title>.*?)' href='(?P<url>.*?)' target=\"_blank\">.*?</a>", p_list)
    for a in a_list:
        video_dict[a.group("title")] = a.group("url")

    info = re.search("<div class=\"info fn-clear\">([\s\S]*?)</div>", text).group(1)
    # print(info)
    info_time = re.search("<span id=\"addtime\">(.*?)</span>", info).group(1)
    info_type = re.search("<dt>类型：</dt><dd>(.*?)</dd>", info).group(1)
    info_details = re.search("<dt>剧情：</dt><dd>(.*?)<a.*?>详细剧情</a></dd>", info).group(1)
    info_starring_connect = re.search("<dl><dt>主演：</dt><dd>([\s\S]*?)</dd>", info).group(1)
    starring_list = re.finditer("<a.*?>(.*?)</a>&nbsp;&nbsp", info_starring_connect)
    starring_str = ""
    for starring in starring_list:
        starring_str += starring.group(1)
    # 名称，主演，时间，类型，剧情，云播链接
    print(info_time, info_type, info_details)
    # print(title, p_list)
    movie["info"] = {"starring": starring_str, "time": info_time, "type": info_type, "details": info_details}
    movie["video_dict"] = video_dict
    movie["title"] = title
    return movie


def spider():
    base_rl = "http://aqdygg.com/dongman/index{}.html"
    movies = []
    i = 1
    for x in range(1, 2):
        # 第一个for循环控制总共有7页
        if x == 1:
            url = base_rl.format("")
        else:
            url = base_rl.format(x)
        detail_urls = get_detail_url(url)
        for detail_url in detail_urls:
            # 第二个for循环遍历一页中电影详情
            movie = parse_detail_page(detail_url)
            print(movie)
            movies.append(movie)
            print("正在爬取第%s部电影" % (i))
            i = i + 1

    # 把数据写入文件
    for movie in movies:
        try:
            with open('moves.csv', 'a+', encoding='utf-8') as file:
                file.write("标题" + '\t' + movie['title'] + '\n')
                info = movie['info']
                file.write("主演" + '\t' + info["starring"] + '\n')
                file.write("时间" + '\t' + info["time"] + '\n')
                file.write("类型" + '\t' + info["type"] + '\n')
                file.write("剧情" + '\t' + info["type"] + '\n')
                video_list = movie['video_dict']
                for key, value in zip(video_list.keys(), video_list.values()):
                    file.write(" " * 5 + key + '\t' + BASE_DOMAIN + value + '\n')

                file.write("=" * 50)
                file.write("\n")
        except:
            with open('moves.csv', 'a+', encoding='utf-8') as file:
                file.write("=" * 50)
                file.write("\n")
            pass


if __name__ == '__main__':
    spider()
