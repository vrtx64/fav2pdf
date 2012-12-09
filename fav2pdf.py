# -*- coding: utf-8 -*-

import re
import sys
from pdf_gen import *
from datetime import date, timedelta, datetime
import requests

import lxml.html


user = ''
site = "habrahabr.ru/users/%s" % user
from_date = '' # 5 августа 2009
to_date = '' # 30 ноября 2010
blog_m = [] #['Android', 'Mobile Development'] только перечисленные блоги

topic_per_page = 10
month = [u'января', u'февраля', u'марта', u'апреля', u'мая', u'июня', u'июля', u'августа', u'сентября', u'октября',
         u'ноября',
         u'декабря']

dr = requests.get('http://' + site + '/favorites/').text

try:
    doc = lxml.html.document_fromstring(dr)
    count = int(doc.xpath('.//div/a/span/span/text()')[0])
except:
    print 'No favorites found. Most likely its a typo in username'
    sys.exit(1)

page = count / topic_per_page + 1

data_finder = doc.xpath('.//div[@class="posts shortcuts_items"]/div/div[1]/text()')

if (to_date != ''):
    td = to_date.split(' ')
    to_date_dt = date(int(td[2]), month.index(td[1]) + 1, int(td[0]))
else:
    to_date_dt = date.today()

if (from_date != ''):
    fd = from_date.split(' ')
    from_date_dt = date(int(fd[2]), month.index(fd[1]) + 1, int(fd[0]))
else:
    from_date_dt = date(2000, 1, 1)

content = u'<br /><div align="center"><h2>Избранное пользователя <a href="http://%s.habrahabr.ru">%s</a></h2> (%s - %s) <br /><br /><strong>Содержание</strong></div><br />' % (
    user, user, from_date_dt.strftime('%d/%m/%y'), to_date_dt.strftime('%d/%m/%y'))

topic = ''
topic_res = ''
topicCount = 0
in_date = 0
topic_m = []

for p in range(1, page + 1):
    print '\nProcessed page %s of %s:' % (p, page)
    dr = requests.get('http://%s/favorites/page%s/' % (site, p)).text

    #get posts
    elems = doc.xpath('.//div[@class="post shortcuts_item"]')
    #get hubs from posts
    hubs = [x.xpath('.//div[@class="hubs"]/a/text()') for x in elems]

    #I think this regexp gets /post/ID/ from the url. Still, we need to proccess elements in list to get the url by get('href') method.
    postLinks = doc.xpath('.//h1[@class="title"]/a[1]')

    postDates = doc.xpath('.//div[@class="posts shortcuts_items"]/div/div[1]/text()')

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

        #here we will get /post/ID/ part of the link
        # check for company/link posts
        url = a.get('href')
        if 'company' in url:
            token = 'post/' + url.split('blog/')[1]
        elif 'linker' in url:
            token = url.split('linker/')[1].replace('go', 'post')
        else:
            token = a.get('href').split('ru/')[1]

        m_link = u'http://m.habrahabr.ru/%s' % token

        #TODO a[0] will not work here, we need to check for specific blog, not list of blogs. Hubs[index] doesnt work at this moment.
        if (topicCount in topic_m) and (hubs[index] in blog_m or blog_m == []):
            td = requests.get(m_link).text
            try:
                td.index(u'<a href="http://m.habrahabr.ru/" accesskey="2">μHabr</a>')
                print '%d Topic: %s->%s' % (topicCount, ', '.join(hubs[index]), url)
                content += u'[%s] <a href="#%d">%s</a><br />' % (', '.join(hubs[index]), topicCount, a.text)

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
                    topicCount, u', '.join(hubs[index]), url, a.text) + topic_res
            except:
                print ' Topic: %s->%s is locked!' % (', '.join(hubs[index]), a.text)

    print '----------------------'
content += topic


#f = open('1.html', 'w')
#f.write(topic)
#f.close()


go(content, user + '.pdf')
