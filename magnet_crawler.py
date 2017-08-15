import requests, re, json, sys, os, imp, codecs, time, threadpool

imp.reload(sys)

tPool = threadpool.ThreadPool(40)
cookie = ''
max_depth = 20
viewed_urls = []
found_magnets = []
ignore_url_param = True
ignore_html_label = True

session = requests.Session()
session.headers.update({'Cookie': cookie})

resource_list = []

if os.path.exists('resource_list.json'):
    with codecs.open('resource_list.json', 'r', 'utf-8') as json_file:
        resource_list = json.loads(json_file.read())
    for resource in resource_list:
        found_magnets.extend(resource['magnets'])

def scan_page(url, depth=0):
    if url in viewed_urls:
        return None
    if (depth > max_depth):
        return None

    print('Entering: ' + url)
    sys.stdout.flush()

    try:
        result = session.get(url, timeout=5)
        print("status:%d" % (result.status_code))
        viewed_urls.append(url)
        if not (result.status_code >= 400 and result.status_code<500):
            result.raise_for_status()
    except Exception as e:
        print("connect error")
        newUrl = [url, depth + 1]
        funcVar = [(newUrl, None)]
        reqs = threadpool.makeRequests(scan_page, funcVar)
        [tPool.putRequest(req) for req in reqs]
        return
    # result_text is html
    result_text = result.content.decode("utf8",errors='ignore')
    # print(result_text.encode("utf8"))
    # 获取页面当中的magnet 并将magnet格式化为magnet_list 页面标题变为page_title 整体化为new_resource
    magnet_list = get_magnet_links(result_text)
    sub_urls = get_sub_urls(result_text, url)
    page_title = get_page_title(result_text)
    new_resource = {'title':page_title, 'magnets': magnet_list}

    # 如果已经在列表里了 直接开始之后的执行
    if new_resource in resource_list:
        funcVar = []
        for sub_url in sub_urls:
            funcVar.append(([sub_url, depth+1], None))
        reqs = threadpool.makeRequests(scan_page, funcVar)
        [tPool.putRequest(req) for req in reqs]
        return

    if (len(magnet_list) > 0):
        # 先将页面标题插入记录最后一次页面标题的文件
        append_title_to_file(page_title, 'magnet_output')
        # 依次将magnet插入记录最后一次magnet的文件
        for magnet in magnet_list:
            print('Found magnet: ' + magnet)
            sys.stdout.flush()
            append_magnet_to_file(magnet, 'magnet_output')
        # 将new_resource对象插入读入内存的文件中
        resource_list.append(new_resource)
        remove_duplicated_resources()
        # 将内存中的文件写入硬盘
        save_json_to_file('resource_list.json')

    # 开始更下一层的遍历
    funcVar = []
    for sub_url in sub_urls:
        funcVar.append(([sub_url, depth+1], None))
    reqs = threadpool.makeRequests(scan_page, funcVar)
    [tPool.putRequest(req) for req in reqs]
    # for sub_url in sub_urls:
    #     Process(target=scan_page, args=(sub_url,depth+1)).start()

def get_sub_urls(result_text, url):
    # 获取当前html中的所有跳转链接
    urls = set(re.findall(r'<a.*?href=[\'"](.*?)[\'"].*?>', result_text))
    sub_urls = []
    for sub_url in urls:
        # 去除此条链接的头尾空格
        sub_url = sub_url.strip()
        # 去除空串和不合要求的链接
        if sub_url == '':
            continue
        if 'javascript:' in sub_url or 'mailto:' in sub_url:
            continue

        if sub_url[0:4] == 'http':
            try:
                if (get_url_prefix(sub_url)[1] != get_url_prefix(url)[1]):
                    continue
            except Exception:
                continue
        # 处理相对路径
        elif sub_url[0:1] == '/':
            sub_url = get_url_prefix(url)[0] + '://' + get_url_prefix(url)[1] + sub_url
        else:
            sub_url = url + '/' + sub_url
        # 处理下一级链接
        sub_url = re.sub(r'#.*$', '', sub_url)
        sub_url = re.sub(r'//$', '/', sub_url)
        if ignore_url_param:
            sub_url = re.sub(r'\?.*$', '', sub_url)
        if not sub_url in viewed_urls:
            sub_urls.append(sub_url)
    return sub_urls

def get_url_prefix(url):
    domain_match = re.search(r'(.*?)://(.*?)/', url)
    if (domain_match):
        return (domain_match.group(1) ,domain_match.group(2))
    else:
        domain_match = re.search(r'(.*?)://(.*)$', url)
        return (domain_match.group(1) ,domain_match.group(2))


def get_magnet_links(result_text):
    if (ignore_html_label):
        result_text = re.sub(r'<[\s\S]*?>', '', result_text)

    result_text = re.sub(r'([^0-9a-zA-Z])([0-9a-zA-Z]{5,30})[^0-9a-zA-Z]{5,30}([0-9a-zA-Z]{5,30})([^0-9a-zA-Z])', r'\1\2\3\4', result_text)

    hashes = list(set(re.findall(r'[^0-9a-fA-F]([0-9a-fA-F]{40})[^0-9a-fA-F]', result_text)))
    hashes.extend(list(set(re.findall(r'[^0-9a-zA-Z]([0-9a-zA-Z]{32})[^0-9a-zA-Z]', result_text))))
    magnets = list(set([('magnet:?xt=urn:btih:' + hash_value).lower() for hash_value in hashes if not ('magnet:?xt=urn:btih:' + hash_value).lower() in found_magnets]))

    found_magnets.extend(magnets)
    return magnets

def get_page_title(result_text):
    match = re.search(r'<title>(.+?)</title>', result_text)
    if match:
        return match.group(1).strip()
    else:
        return ''

def append_magnet_to_file(magnet, filename):
    with codecs.open(filename, 'a+', 'utf-8') as output_file:
        output_file.write(magnet + '\n')

def append_title_to_file(title, filename):
    with codecs.open(filename, 'a+', 'utf-8') as output_file:
        output_file.write(title + '\n')

def remove_duplicated_resources():
    global resource_list
    new_resource_list = []
    for resource in resource_list:
        add_flag = True
        for added_resource in new_resource_list:
            if added_resource['title'] == resource['title']:
                add_flag = False
                added_resource['magnets'].extend(resource['magnets'])
                added_resource['magnets'] = list(set(added_resource['magnets']))
                break
        if add_flag:
            new_resource_list.append(resource)
    resource_list = new_resource_list

def save_json_to_file(filename):
    with codecs.open(filename, 'w+', 'utf-8') as output_file:
        output_file.write(json.dumps(resource_list, indent=4, sort_keys=True, ensure_ascii=False))

def endProgram(startTime, maxTime):
    while time.time() - startTime < maxTime:
        pass
    print("Time is not enough!")
    os._exit(0)

def main():
    startTime = time.time()
    # print("Now it has started!")
    # print('Enter a website url to start.')
    # root_url = input()
    root_url = "http://www.llss.me/wp/23897.html/"
    if not '://' in root_url:
        root_url = 'http://' + root_url
    #with open('', 'w+') as output_file:
    #    output_file.write('')
    times = [([startTime, 1200], None)]
    reqt = threadpool.makeRequests(endProgram, times)
    timepool = threadpool.ThreadPool(1)
    [timepool.putRequest(req) for req in reqt]

    urls = [root_url]
    reqs = threadpool.makeRequests(scan_page, urls)
    [tPool.putRequest(req) for req in reqs]
    tPool.wait()
    print("cost %d s" % (time.time() - startTime))
    os._exit(0)

if __name__ == '__main__':
    main()


