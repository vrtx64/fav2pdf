# -*- coding: utf-8 -*-

import urllib
import re
from pdf_gen import *
from datetime import date


user = 'vrtx'
site = user + '.habrahabr.ru'
from_date = '' # 5 августа 2009
to_date = '' # 30 ноября 2010
blog_m = [] #['Android', 'Mobile Development'] только перечисленные блоги


topic_per_page = 10
month = ['января','февраля','марта','апреля','мая','июня','июля','августа','сентября','октября','ноября','декабря']

dump = urllib.urlopen('http://' + site + '/favorites/')
dr = dump.read()

try:
	count = int(re.findall('Избранное \((.*)\)<\/a>', dr)[0])
except:
	count = 0

page = count / topic_per_page + 1

data_finder = re.compile('(\d+)\s(\D+)\s(\d{4})')

if (to_date != ''):
	td = data_finder.findall(to_date)[0]
	to_date_dt = date(int(td[2]), month.index(td[1])+1, int(td[0]))
else:
	to_date_dt = date.today()

if (from_date != ''):
	fd = data_finder.findall(from_date)[0]
	from_date_dt = date(int(fd[2]), month.index(fd[1])+1, int(fd[0]))
else:
	from_date_dt = date(2000, 1, 1)

content = '<br /><div align="center"><h2>Избранное пользователя <a href="http://%s.habrahabr.ru">%s</a></h2> (%s - %s) <br /><br /><strong>Содержание</strong></div><br />' % (user, user, from_date_dt.strftime('%d/%m/%y'), to_date_dt.strftime('%d/%m/%y'))

topic = ''
topic_res = ''
i = 0
in_date = 0
topic_m = []

for p in range(1,page+1):
	
	print '\nProcessed page %s of %s:' % (p, page)
	dump = urllib.urlopen('http://%s/favorites/page%s' % (site, p))
	dr = dump.read()

	res = re.findall('class="blog">(.*)<\/a> &rarr\s*\D*\s+<a \D*href="(.*)"\D* class="topic">(.*)<\/a>', dr) #[^(<span class="locked"></span>)]
	
	data = re.findall('<div class="published">\D+\s*(\d+)\s(\D+)\s(\d{4}).*</span>', dr)
	
	for dd in data:
		in_date += 1
		d = date(int(dd[2]), month.index(dd[1])+1, int(dd[0]))
		if (d >= from_date_dt and d <= to_date_dt):
			topic_m.append(in_date)
			
	print '----------------------'
	#0 - blog; 1 - link; 2 - topic;
	for a in res:
		i += 1
		
		m_link = 'http://m.habrahabr.ru/post%s' % (re.findall('/\d+/', a[1])[0])
		
		if (i in topic_m) and ((a[0] in blog_m) or (blog_m == [])):

			topic_dump = urllib.urlopen(m_link)
			td = topic_dump.read()
			try:
				td.index('<div class="tm"><a href="http://m.habrahabr.ru/" accesskey="2">μHabr</a>')
				print '%d Topic: %s->%s' % (i, a[0], a[2])
				content += '[%s] <a href="#%d">%s</a><br />' % (a[0], i, a[2])

				#td = re.sub('<div class="m">.*,', '<div class="m"><a href="'+ autor +'.habrahabr.ru">'+ autor +'</a>,' , td)
				t_start = td.find('<div class="txt">')
				t_stop = td.find('<div class="adv"><script>')
				topic_res = td[t_start:t_stop]
				autor = re.findall('<div class="m">(.*),', topic_res)[0]
				topic_res= re.sub('<div class="m">(.*),', '<div class="m"><a href="http://%s.habrahabr.ru">%s</a>,' % (autor, autor) , topic_res)
				topic_res = re.sub('\s<br/>\s*\S*<br/>', '<br/>', topic_res)
				topic_res = topic_res.replace('align="left"/>', '/>')
				topic_res = topic_res.replace('align="center"', 'align="middle"')
				
				topic_res = re.sub('/>\s*<img', '/><br/><img', topic_res)
				
				topic = topic + '<div><pdf:nextpage /></div><h2><a name="%d">[%s] </a><a href="%s">%s</a></h2><br><br>' % (i, a[0], a[1], a[2]) + topic_res	
			except:	
				print ' Topic: %s->%s is locked!' % (a[0], a[2])


	print '----------------------'
content = content + topic


#f = open('1.html', 'w')
#f.write(topic)
#f.close()


go(content, user+'.pdf')