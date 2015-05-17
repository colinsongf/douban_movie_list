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
            'Origin': 'https://www.douban.com',
            'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36',
            'Referer' : 'https://www.douban.com/accounts/login',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection' : 'Keep-Alive'
        }
        self.post = {
            'source':'None',
            'form_email':'uare@sina.com',
            'form_password':'8271152',
            'remember':'on',
            'login':'登陆',
            'redir':'https://www.douban.com',
            'captcha-solution':'fiction',
            'captcha-id':'Qqa1NTqCwr1xk5Vb9VZk9KpA:en'
        }
        

        self.postdata = urllib.urlencode(self.post)
        self.proxy = urllib2.ProxyHandler({'http':self.proxyURL})
        self.cookie = cookielib.LWPCookieJar()
        self.cookieHandler = urllib2.HTTPCookieProcessor(self.cookie)
        self.opener = urllib2.build_opener(self.cookieHandler,self.proxy,urllib2.HTTPHandler)

        self.newCookie = cookielib.CookieJar()
        self.newOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.newCookie))


        
        self.loginWithIdenCode()

    def loginWithIdenCode(self):
        request = urllib2.Request(self.loginUrl,self.postdata,self.loginHeaders)
        response = self.opener.open(request)
        content = response.read()
        # print content

    

        with open("first_try.html",'w') as cf:
            cf.write(content)

        pattern = re.compile('<img id="captcha_image" src="(.*?)"',re.S)

        # print content
        
        matchResult = re.search(pattern,content)

        if matchResult:
            print "Image Code Needed."
            idenCodeSrc= matchResult.group(1)


            pattern2 = re.compile('id=(.*?)&amp',re.S)
            idenCodeId = re.search(pattern2,idenCodeSrc)
            idenCodeId = idenCodeId.group(1)
                        

            webbrowser.open_new_tab(idenCodeSrc)
            
            self.post['captcha-id'] = idenCodeId

            
            while True:
                if self.TryInputIdenCode():
                    break
        else:
            print "No Image Code Needed"


    def TryInputIdenCode(self):

        checkcode = raw_input('Input the Image Code: ')        
        self.post['captcha-solution'] = checkcode
        print checkcode
        self.postdata = urllib.urlencode(self.post)

        # self.loginUrl="http://accounts.douban.com/login?uid=51431818&alias=uare%40sina.com&redir=https%3A%2F%2Fwww.douban.com%2F&source=None&error=1011"

        request = urllib2.Request(self.loginUrl,self.postdata,self.loginHeaders)
        response = self.opener.open(request)

        content = response.read()
        # print content
        resultpattern = re.compile('验证码不正确',re.S)
        isWrongCode = re.search(resultpattern,content)

        with open('second_try.html','w') as rf:
            rf.write(content)

        if isWrongCode:
            print "Wrong Image Code, Please Retype"
            return False
        else:
            print "Correct Image Code. Login Successfully"
            return True

    def getPage(self):

        redheartUrl_part1='http://douban.fm/mine'
        current_page = '#!type=liked'
        #readheartUrl = redheartUrl_part1+current_page
        redheartUrl = "http://douban.fm/mine?type=liked#!type=liked"
        redheartUrl = "http://douban.fm/mine#!type=played"

        movieUrl = "http://movie.douban.com/mine"

        headers = {
            'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36',
            'Host':'douban.fm',
            'Connection' : 'Keep-Alive',
            'Referer':'http://douban.fm/mine'

        }

        while True:
            # request = urllib2.Request(redheartUrl,headers = headers)          
            result = self.opener.open(redheartUrl)
            # request = urllib2.Request(redheartUrl,headers = headers)
            # result = self.newOpener.open(request)
            with open("songlist.html",'w') as rf:

                rf.write(result.read())

            moviePage = self.opener.open(movieUrl)

            with open("movielist.html","w") as mf:
                mf.write(moviePage.read())


            break
       
        # print result.read()#.decode('gbk')
 
 
sdu = RHS()
sdu.getPage()

