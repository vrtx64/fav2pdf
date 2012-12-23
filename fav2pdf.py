# -*- coding: utf-8 -*-

import re
import sys
from pdf_gen import *
from datetime import date, timedelta, datetime
import requests
from multiprocessing import Pool
import lxml.html


def countFavorites(pageText):
    try:
        pageTree = lxml.html.document_fromstring(pageText)

        profilepage = requests.get('http://' + site).text
        if u'read-only' in profilepage:
            count = int(pageTree.xpath('.//td/a/span/span/text()')[0])
        else:
            count = int(pageTree.xpath('.//div/a/span/span/text()')[0])
            # Read-only accounts have different page layout, so it needs different handling

        return count
    except:
        print 'No favorites found. Most likely its a typo in username'
        sys.exit(1)


def ProcessPost(linkElem, content, topic):
    #here we will get /post/ID/ part of the link
    # check for company/link posts
    url = linkElem.get('href')
    if 'company' in url:
        token = 'post/' + url.split('blog/')[1]
    elif 'linker' in url:
        token = url.split('linker/')[1].replace('go', 'post')
    else:
        token = linkElem.get('href').split('ru/')[1]
    m_link = u'http://m.habrahabr.ru/%s' % token
    if len(set(blog_m) & set(hubs[index])) > 0:
        hubFlag = True
    else:
        hubFlag = False
    if (topicCount in topic_m) and (hubFlag or blog_m == []):
        td = requests.get(m_link).text
        try:
            td.index(u'<a href="http://m.habrahabr.ru/" accesskey="2">μHabr</a>')
            print '%d Topic: %s->%s' % (topicCount, ', '.join(hubs[index]), url)
            content += u'[%s] <a href="#%d">%s</a><br />' % (', '.join(hubs[index]), topicCount, linkElem.text)

            t_start = td.find('<div class="txt">')
            t_stop = td.find('<div class="adv">')
            topic_res = td[t_start:t_stop]
            autor = re.findall('<div class="m">\n\t\t\t\n\t\t\t(.*),', topic_res)[0]
            topic_res = re.sub('<div class="m">\n\t\t\t\n\t\t\t(.*),',
                '<div class="m"><a href="http://%s.habrahabr.ru">%s</a>,' % (autor, autor), topic_res)
            topic_res = re.sub('\s<br/>\s*\S*<br/>', '<br/>', topic_res)
            topic_res = topic_res.replace('align="left"/>', '/>')
            topic_res = topic_res.replace('align="center"', 'align="middle"')

            topic_res = re.sub('/>\s*<img', '/><br/><img', topic_res)

            topic = topic + u'<div><pdf:nextpage /></div><h2><a name="%d">[%s] </a><a href="%s">%s</a></h2><br><br>' % (
                topicCount, u', '.join(hubs[index]), url, linkElem.text) + topic_res

            return content, topic
        except:
            print ' Topic: %s->%s is locked!' % (', '.join(hubs[index]), linkElem.text)


if __name__ == "__main__":
    user = 'JazzCore'
    threads = 4 # Кол-во потоков. При большом кол-ве сильно возрастает потребление памяти. Рекоммендуется 4-8 потоков
    from_date = u'' # 5 августа 2009
    to_date = u'' # 30 ноября 2010
    blog_m = [] #[u'Android', u'Mobile Development'] только перечисленные блоги. Должны быть юникодные не забывать 'u' перед строкой. Звездочки писать не надо.

    site = "habrahabr.ru/users/%s" % user
    topic_per_page = 10
    month = [u'января', u'февраля', u'марта', u'апреля', u'мая', u'июня', u'июля', u'августа', u'сентября', u'октября',
             u'ноября',
             u'декабря']

    pageText = requests.get('http://' + site + '/favorites/').text

    count = countFavorites(pageText)

    page = count / topic_per_page + 1

    if to_date != '':
        td = to_date.split(' ')
        to_date_dt = date(int(td[2]), month.index(td[1]) + 1, int(td[0]))
    else:
        to_date_dt = date.today()

    if from_date != '':
        fd = from_date.split(' ')
        from_date_dt = date(int(fd[2]), month.index(fd[1]) + 1, int(fd[0]))
    else:
        from_date_dt = date(2000, 1, 1)

    topic_res = ''
    topicCount = 0
    in_date = 0
    topic_m = []

    pool = Pool(processes=threads)

    for p in range(1, page + 1):
        topic = ''
        tableOfContents = u'<br /><div align="center"><h2>Избранное пользователя <a href="http://%s.habrahabr.ru">%s</a>'\
                          u'</h2> (%s - %s) <br /><br /><strong>Содержание</strong></div><br />' %\
                          (user, user, from_date_dt.strftime('%d/%m/%y'), to_date_dt.strftime('%d/%m/%y'))

        print '\nProcessed page %s of %s:' % (p, page)
        pageText = requests.get('http://%s/favorites/page%s/' % (site, p)).text

        #get posts
        pageTree = lxml.html.fromstring(pageText)
        elems = pageTree.xpath('.//div[@class="posts shortcuts_items"]/div')
        #get hubs from posts
        hubs = [x.xpath('.//div[@class="hubs"]/a/text()') for x in elems]

        postLinks = pageTree.xpath('.//h1[@class="title"]/a[1]')

        postDates = pageTree.xpath('.//div[@class="posts shortcuts_items"]/div/div[1]/text()')

        for dd in postDates:
            in_date += 1

            parts = dd.strip(' ').split(' ')
            if u'вчера' in dd:
                d = date.today() - timedelta(1)
            elif u'сегодня' in dd:
                d = date.today()
            else:
                if re.search('20[0-9]{2}', dd):
                    d = date(int(parts[2]), month.index(parts[1]) + 1, int(parts[0]))
                else:
                    d = date(datetime.now().year, month.index(parts[1]) + 1, int(parts[0]))

            if from_date_dt <= d <= to_date_dt:
                topic_m.append(in_date)

        print '----------------------'
        for index, a in enumerate(postLinks):
            topicCount += 1

            #Retrieve all data from post and append it to string with page content
            tableOfContents, topic = ProcessPost(a, tableOfContents, topic)

        print '----------------------'
        tableOfContents += topic
        pool.apply_async(go, args=[tableOfContents, user + '-tst3-' + str(p) + '.pdf'])

    print 'Wait until all pages are saved'

    pool.close()
    pool.join()

    print 'Done!'
    #f = open('1.html', 'w')
    #f.write(topic)
    #f.close()

    #go(content, user + '.pdf')
