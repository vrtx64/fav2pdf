# -*- coding: utf-8 -*-

import ho.pisa as pisa

header = '''

<html>
<meta http-equiv="content-type" content="text/html; charset=utf-8"/>
<head>

<style>

@page {

	margin: 40px;
	margin-left: 60px;
	margin-bottom: 70px;
	@frame footer {
		-pdf-frame-content: footerContent;
		bottom: 10px;
		margin-left: 60px;
		margin-right: 40px;
		height: 40px;
  }

}

@font-face {
	font-family: courier;
	src: url(fonts/Courier_New.ttf);
}

@font-face {
	font-family: courier;
	src: url(fonts/Courier_Bold.ttf);
	font-weight: bold;
}

@font-face {
	font-family: courier;
	src: url(fonts/Courier_Bold_Italic.ttf);
	font-weight: bold;
	font-style: italic;
}

@font-face {
	font-family: courier;
	src: url(fonts/Courier_Italic.ttf);
	font-style: italic;
}

@font-face {
	font-family: verdana;
	src: url(fonts/Verdana.ttf);
}

@font-face {
	font-family: verdana;
	src: url(fonts/Verdana_Bold.ttf);
	font-weight: bold;
}

@font-face {
	font-family: verdana;
	src: url(fonts/Verdana_Italic.ttf);
	font-style: italic;
}

@font-face {
	font-family: verdana;
	src: url(fonts/Verdana_Bold_Italic.ttf);
	font-style: italic;
	font-weight: bold;
}


img {
	font-family: sans;

}

body, div {
	font-family: verdana;
	font-size: 14px;
	color:#000;
	background:#fff;
}


a[href] { color: #6da3bd; }
a[name] { color: #000000; font-size: 150%; text-decoration:none}

fieldset {border:0 solid transparent;}
input, select, textarea {
	font-size: 100%;
	font-family: verdana;
}

blockquote {
	border-left:2px solid #bbb;
	margin: .83em 10;
	padding-left:15px;
	clear: both;
}

ul,ol,li,h1,h2,h3,h4,h5,h6,pre,form,body,html,blockquote,fieldset,dl,dt,dd,caption {margin:0; padding:0;}
ul,ol {list-style: none;}
pre,code {font-size: 1em;}

h1, h2, h3, h4, h5, h6 {
	color:#999999;
	font-family: verdana;
	font-weight:normal;
	margin:0 0 0 0;
	padding:0;
}

h1 {
	font-size:162.5%;
	letter-spacing:-1px;
	margin-bottom:0.7em;
}

h2 {
	font-size:150%;
}

h3 {
	font-size: 137.5%;
}

h4 {
	font-size: 120%;
}

h5 {
	font-size: 110%;
}

h6 {
	font-size: 100%;
}

pre {
	font-size: 80%;
}
	 
</style>
</head>
<body>


<div align="center"><img src="http://habrahabr.ru/i/logo.gif"></div>'''

footer = '''

  <div id="footerContent" align="right">
  <hr>
    Страница #<pdf:pagenumber>
  </div>
</body>
</html>
'''


def go(content, filename):
	print '\n Prepare PDF...\n'
	content = header + content + footer

	#pisa.showLogging()
	pisa.CreatePDF(content, file(filename, 'wb'))