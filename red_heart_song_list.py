# -*- coding:utf-8 -*-
#coding=utf-8 
__author__="Li Ding"

import urllib
import urllib2
import cookielib
import re
import webbrowser
import mechanize
 

class RHS:
 
    def __init__(self,email,password):
        self.loginUrl = "https://www.douban.com/accounts/login"
        
        #Proxy URL, in case your own id is banned by douban.fm
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
            'form_email':email,
            'form_password':password,
            'remember':'on',
            'login':'登陆',
            'redir':'https://www.douban.com',
            'captcha-solution':'fiction',
            'captcha-id':'Qqa1NTqCwr1xk5Vb9VZk9KpA:en'
        }


        #Construct the cookie used to crawl douban related webpage
        self.postdata = urllib.urlencode(self.post)
        self.proxy = urllib2.ProxyHandler({'http':self.proxyURL})
        self.cookie = cookielib.LWPCookieJar()
        self.cookieHandler = urllib2.HTTPCookieProcessor(self.cookie)
        self.opener = urllib2.build_opener(self.cookieHandler,self.proxy,urllib2.HTTPHandler)

        # self.newCookie = cookielib.CookieJar()
        # self.newOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.newCookie))


        #Login with Image Code
        self.loginWithIdenCode()

    def loginWithIdenCode(self):

        #Attempt to login in, for the first try
        request = urllib2.Request(self.loginUrl,self.postdata,self.loginHeaders)
        response = self.opener.open(request)

        content = response.read()

    

        with open("first_try.html",'w') as cf:
            cf.write(content)

        #See if Image Code is needed
        pattern = re.compile('<img id="captcha_image" src="(.*?)"',re.S)       
        matchResult = re.search(pattern,content)

        if matchResult:
            print "Image Code Needed."
            idenCodeSrc= matchResult.group(1)
            
            while True:
                #Try to login with image code
                if self.TryInputIdenCode(idenCodeSrc):
                    break
        else:            
            print "No Image Code Needed. Login Successfully."


    def TryInputIdenCode(self,idenCodeSrc):

        #Obtain the Image Code url
        pattern2 = re.compile('id=(.*?)&amp',re.S)
        idenCodeId = re.search(pattern2,idenCodeSrc)
        idenCodeId = idenCodeId.group(1)
        self.post['captcha-id'] = idenCodeId
                        
        #Show the image in the web-browser and type in it in the command line manually
        webbrowser.open_new_tab(idenCodeSrc)    
        checkcode = raw_input('Input the Image Code shown in the webbrowser: ')        
        self.post['captcha-solution'] = checkcode
        self.postdata = urllib.urlencode(self.post)

        #Check if the Image Code typed from user is correct
        request = urllib2.Request(self.loginUrl,self.postdata,self.loginHeaders)
        response = self.opener.open(request)
        content = response.read()
        resultpattern = re.compile('验证码不正确',re.S)
        isWrongCode = re.search(resultpattern,content)

        with open('second_try.html','w') as rf:
            rf.write(content)

        if isWrongCode:
            print "Wrong Image Code, Please Retype"
            ICpattern = re.compile('<img id="captcha_image" src="(.*?)"',re.S)

            matchResult = re.search(ICpattern,content)
            idenCodeSrc= matchResult.group(1)
            #Retype the Image Code
            return self.TryInputIdenCode(idenCodeSrc)
            return False
        else:
            print "Correct Image Code. Login Successfully"
            return True

    def getPage(self):

        br = mechanize.Browser()
        br.set_cookiejar(self.cookie)

        br.set_handle_equiv(True)
        br.set_handle_gzip(True)
        br.set_handle_redirect(True)
        br.set_handle_referer(True)
        br.set_handle_robots(False)




        #readheartUrl = redheartUrl_part1+current_page
        redheartUrl = "http://douban.fm/mine#!type=liked&start=15"

        movieUrl = "http://movie.douban.com/people/51431818/collect"

        headers = {
            'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36',
            'Host':'douban.fm',
            'Connection' : 'Keep-Alive',
            'Referer':'http://douban.fm/mine'

        }

        
        response = br.open("http://douban.fm/mine#!type=liked")

        for link in br.links(text_regex='不再播放51首'):
            print link

        req=br.click_link(text_regex='不再播放51首')

        print req
        response = br.open(req)


        with open("mech_result.html",'w') as mf:
            mf.write(response.read())

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
       
if __name__ == '__main__':

    #Provide your email and password for Douban.com
    # user_email=raw_input("Input Your Email: ")
    user_email = "uare@sina.com"
    # user_password=raw_input("Input Your Password: ")
    user_password = "8271152"

    sdu = RHS(email=user_email,password=user_password)
    sdu.getPage()

