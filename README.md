# Find magnets on [HACG](http://www.llss.me)
Run magnet_crawler.py and the output file is resource_list.json.

_Actually, I haven't read this code seriously and just make it run on python3._

# Environment
- win10
- python3
- what is necessary to connect to the HACG


## 2017_8_14
      After downloading the source code, the run-time procedures out some wrong, because some places do not support python3 code, there are also a problem with the file code. They have been fixed.
      To tell the truth, now the function is still too little, but the corresponding, the code is also very simple, can be used as practice hand, just started learning python, just can now learn to use.
Free to add some features:
- Multithreading(to speed up)
- Borrow Baidu cloud link(some multimedia resources are on it)
- Adapt more sites(use this on more website)

## Original source code comes from [Hello Old Driver](https://github.com/Chion82/hello-old-driver)([琉璃神社](http://www.llss.me) 定时同步爬虫脚本（非官方）。)
----------------
文章内容版权归 [琉璃神社](http://www.llss.me) 所有，本仓库不提供资源。  
----------------
# _Plan_
## 2017_8_15
多线程
- [X] 添加多线程功能
- [X] 程序开始时设定线程数目
- [ ] 将线程模块换为mul的
- [ ] 每个线程最长存活时间
- [ ] 添加互斥锁

输入
- [ ] 限制扫描的最多url数目

扒取
- [ ] 可扒取其他网站

日志功能
- [X] 每次执行向日志文件中添加日志信息
    - [X] 起始页面的title
    - [X] 执行结果
    - [X] 起始、结束时间
    - [X] 所用时间
    - [X] 扫描的url数目
    - [X] 扫描的magnet数目
    - [X] 新添magnet数目