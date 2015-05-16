# -*- coding:utf-8 -*-
#coding=utf-8 

import urllib
import urllib2
import cookielib
import re
import webbrowser
 

class RHS:
 
    def __init__(self):
        self.loginUrl = "https://www.douban.com/accounts/login"
        # self.cookies = cookielib.CookieJar()
        self.proxyURL = 'http://61.233.25.166:80'
        self.loginHeaders =  {
            'Host':'accounts.douban.com',
            'Origin': 'http://accounts.douban.com',
            'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36',
            'Referer' : 'http://www.douban.com/accounts/login?redir=http://www.douban.com/doumail/',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection' : 'Keep-Alive'
        }
        self.post = {
        	'source':'None',
        	'form_email':'uare@sina.com',
        	'form_password':'8271152',
        	'remember':'on',
        	'login':'登陆',
        	'redir':'http://www.douban.com/doumail/'
         }

        self.postdata = urllib.urlencode(self.post)
        self.proxy = urllib2.ProxyHandler({'http':self.proxyURL})
        self.cookie = cookielib.LWPCookieJar()
        self.cookieHandler = urllib2.HTTPCookieProcessor(self.cookie)
        self.opener = urllib2.build_opener(self.cookieHandler,self.proxy,urllib2.HTTPHandler)

        self.newCookie = cookielib.CookieJar()
        self.newOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.newCookie))


        # self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookies))

        self.loginWithIdenCode()

    def loginWithIdenCode(self):
    	request = urllib2.Request(self.loginUrl,self.postdata,self.loginHeaders)
    	response = self.opener.open(request)
    	content = response.read()
    	# print content

    	pattern = re.compile('<img id="captcha_image" src="(.*?)"',re.S)
    	
    	matchResult = re.search(pattern,content)
    	idenCodeSrc= matchResult.group(1)

    	pattern2 = re.compile('id=(.*?)&amp',re.S)
    	idenCodeId = re.search(pattern2,idenCodeSrc)
    	idenCodeId = idenCodeId.group(1)
    	print idenCodeId
    	

    	webbrowser.open_new_tab(idenCodeSrc)
    	
        self.post['captcha_id'] = idenCodeId

        
        while True:
        	if self.TryInputIdenCode():
        		break;


    def TryInputIdenCode(self):

    	checkcode = raw_input('Input the Image Code: ')        
        self.post['captcha_solution'] = checkcode
        print checkcode
        self.postdata = urllib.urlencode(self.post)

        request = urllib2.Request(self.loginUrl,self.postdata,self.loginHeaders)
        response = self.opener.open(request)

        content = response.read()
        # print content
    	resultpattern = re.compile(u'\u9a8c\u8bc1\u7801\u4e0d\u6b63\u786e',re.S)
    	result = re.search(resultpattern,content)

    	with open('response.txt','w') as rf:
    		rf.write(content)

    	if result:
    		print "Wrong Image Code"
    		return False
    	else:
    		print "Correct Image Code"
    		return True

    def getPage(self):

    	redheartUrl_part1='http://douban.fm/mine'
    	current_page = '#!type=liked'
    	#readheartUrl = redheartUrl_part1+current_page
    	redheartUrl = "http://book.douban.com/mine?icn=index-nav"

    	headers = {
            'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36',
            'Host':'douban.fm',
            'Connection' : 'Keep-Alive',
            'Referer':'http://douban.fm/mine'

        }

    	while True:
    		request = urllib2.Request(redheartUrl,headers = headers)    		
    		result = self.opener.open(redheartUrl)
    		break
       
        print result.read()#.decode('gbk')
 
 
sdu = RHS()
sdu.getPage()

