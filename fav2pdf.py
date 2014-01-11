#!/usr/bin/python2
# -*- coding: utf-8 -*-

import re
import argparse
import os
import sys
from pdf_gen import *
from datetime import date, timedelta, datetime
import requests

import lxml.html


def parseTopic(url):
    td = requests.get(url).text
    td.index(u'<a href="http://m.habrahabr.ru/" accesskey="2">μHabr</a>')
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

    cmts_start = td.find('<div class="cmts">')
    cmts_stop = td.find('<div class="bm">')
    cmts_res = td[cmts_start:cmts_stop]

    return topic_res, cmts_res


def save(dest_dir=u'.', user='none', from_date=u'', to_date=u'', 
    all_in_one=False, save_comments=True, create_symlinks=True, only_hubs = []):
    # user = 'icoz'
    site = "habrahabr.ru/users/%s" % user
    # from_date = u''  # 5 августа 2009
    # to_date = u''  # 30 ноября 2010
    #[u'Android', u'Mobile Development'] только перечисленные блоги. Должны быть юникодные, не забывать 'u' перед строкой. Звездочки писать не надо.

    topic_per_page = 10
    month = [
        u'января', u'февраля', u'марта', u'апреля', u'мая', u'июня', u'июля', u'августа', u'сентября', u'октября',
        u'ноября',
        u'декабря']

    dr = requests.get('http://' + site + '/favorites/').text
    DIR_PDF = dest_dir + '/pdf'
    DIR_POSTS = DIR_PDF + '/posts'
    DIR_HUBS = DIR_PDF + '/hubs'
    if not all_in_one:
        if not os.path.exists(DIR_PDF):
            os.mkdir(DIR_PDF)
        if not os.path.exists(DIR_POSTS):
            os.mkdir(DIR_POSTS)
        if create_symlinks:
            if not os.path.exists(DIR_HUBS):
                os.mkdir(DIR_HUBS)

    try:

        doc = lxml.html.document_fromstring(dr)

        profilepage = requests.get('http://' + site).text
        profiledoc = lxml.html.document_fromstring(profilepage)
        if u'read-only' in profilepage:
            count = int(doc.xpath('.//td/a/span/span/text()')[0])
        else:
            count = int(doc.xpath('.//div/a/span/span/text()')[0])
        # Read-only accounts have different page layout, so it needs different
        # handling
    except:
        print 'No favorites found. Most likely its a typo in username'
        sys.exit(1)

    page = count / topic_per_page + 1

    data_finder = doc.xpath(
        './/div[@class="posts shortcuts_items"]/div/div[1]/text()')

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
    content_body = u''
    topic = ''
    topic_res = ''
    topicCount = 0
    in_date = 0
    topic_m = []

    for p in range(1, page + 1):
        print '\nProcessed page %s of %s:' % (p, page)
        dr = requests.get('http://%s/favorites/page%s/' % (site, p)).text

        # get posts
        doc = lxml.html.fromstring(dr)
        elems = doc.xpath('.//div[@class="posts shortcuts_items"]/div')
        # get hubs from posts
        hubs = [x.xpath('.//div[@class="hubs"]/a/text()') for x in elems]

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
                    d = date(int(parts[2]), month.index(
                        parts[1]) + 1, int(parts[0]))
                else:
                    d = date(datetime.now().year, month.index(
                        parts[1]) + 1, int(parts[0]))

            if from_date_dt <= d <= to_date_dt:
                topic_m.append(in_date)

        print '----------------------'
        for index, a in enumerate(postLinks):
            topicCount += 1

            # here we will get /post/ID/ part of the link
            # check for company/link posts
            url = a.get('href')
            if 'company' in url:
                token = 'post/' + url.split('blog/')[1]
            elif 'linker' in url:
                token = url.split('linker/')[1].replace('go', 'post')
            else:
                token = a.get('href').split('ru/')[1]
            # get post id for saving
            id = token.split('post/')[1]
            if id[-1] == "/":
                id = id[:-1]

            m_link = u'http://m.habrahabr.ru/%s' % token

            if len(set(only_hubs) & set(hubs[index])) > 0:
                hubFlag = True
            else:
                hubFlag = False

            if (topicCount in topic_m) and (hubFlag or only_hubs == []):
                try:
                    print '%d Topic: %s->%s' % (topicCount, ', '.join(hubs[index]), url)
                    if all_in_one:
                        content += u'[%s] <a href="#%d">%s</a><br />' % (
                            ', '.join(hubs[index]), topicCount, a.text)
                    topic_res, cmts_res = parseTopic(m_link)
                    # format topic
                    topic = u'<h2><a name="%d">[%s] </a><br><a href="%s">%s</a></h2><br><br>' % (
                        topicCount, u', '.join(hubs[index]), url, a.text) + topic_res
                    # ... and comments
                    if save_comments:
                        topic += cmts_res
                    if all_in_one:
                        content_body += topic
                    else:
                        go(topic, DIR_POSTS + '/' + id + '.pdf')
                        # create symlinks
                        if create_symlinks:
                            for hub in hubs[index]:
                                if not os.path.exists(DIR_HUBS + '/' + hub):
                                    os.mkdir(DIR_HUBS + '/' + hub)
                                os.symlink(
                                    '../../posts/' + id + '.pdf', DIR_HUBS + '/' + hub + "/" + id + '.pdf')
                except:
                    print ' Topic: %s->%s is locked!' % (', '.join(hubs[index]), a.text)

        print '----------------------'
    if all_in_one:
        go(content+content_body, dest_dir + '/' + user + '.pdf')


def main():
    p = argparse.ArgumentParser(description=u'Tool for save favorite posts from habrahabr.ru in pdf''s')
    p.add_argument('user', type=str, help="habrahabr.ru username")
    p.add_argument('-d', '--output-dir', default='.', type=str, help="Directory for output")
    p.add_argument('--from-date', type=str, default=u'', help='From date')
    p.add_argument('--to-date', type=str, default=u'', help='To date')
    p.add_argument('--all-in-one', action='store_true', help='Save all posts in one PDF-file')
    p.add_argument('--only_hub', type=str, action='append', help='Save only posts from hubs. For multiple: "--only_hub Hub1 --only_hub Hub2"')
    p.add_argument('--no-comments',action='store_true', help='Dont save comments from posts')
    p.add_argument('--no-symlinks',action='store_true', help='Dont create symlinks to posts')
    args = p.parse_args()
    print (args)
    save(dest_dir = args.output_dir, user=args.user, from_date=args.from_date, to_date=args.to_date,
        only_hubs=args.only_hub, all_in_one=args.all_in_one, save_comments=not args.no_comments,
        create_symlinks = not args.no_symlinks)

if __name__ == '__main__':
    main()
