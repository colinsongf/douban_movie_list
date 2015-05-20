# -*- coding:utf-8 -*-
#coding=utf-8 
__author__="Li Ding"

import urllib
import urllib2
import cookielib
import re
import webbrowser
import mechanize
from bs4 import BeautifulSoup
import MySQLdb as mdb
import sys



class OneMovie:
    def __init__(self,movieitem):
        self.movie = movieitem
        self.title = self.getTitle()

    def getTitle(self):
        title = self.movie.select(".info .title a em")[0].string.encode('utf-8')
        return title.split("/")
    def getChineseTitle(self):
        return self.title[0]
    def getEnglishTitle(self):
        if len(self.title)==2:
            return self.title[1]
        else:
            return "N/A"

    def getUrl(self):
        return self.movie.select(".info .title a")[0].get("href")
    def getDebut(self):
        various_info = self.movie.select(".info .intro")[0].string.encode('utf-8')
        return various_info.split('/')[0]

    def getWatchedDate(self):
        return self.movie.select(".info .date")[0].string
    def getComment(self):
        comment = self.movie.select(".info .comment")
        if comment:
            return comment[0].string.encode('utf-8')
        else:
            return "N/A"



class MoviePage:
    def __init__(self,page):
        self.soup = BeautifulSoup(page)
        self.hasNextPage=True
        self.nextPage=self.getNext()
        

    def getNext(self):
        #To see if has next page
        nextLink = self.soup.select(".paginator .next link")
        if nextLink:
            return nextLink[0].get("href")
        else:
            self.hasNextPage = False
            return False

    def getMovies(self):
        #Return Movies
        for item in self.soup.select(".grid-view .item"):
            yield OneMovie(item)
 

class DoubanMovies:
 
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


        #Login with Image Code
        self.loginWithIdenCode()

        self.movie_storage = movieStorage()

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

    def getMovieInfo(self):
        starting_url =  "http://movie.douban.com/people/51431818/collect"

        intended_page = starting_url
        f = open("movie_info.txt",'w')
        
        while True:
            #Crawl the Current Page and construct a MoviePage object
            print("Crawling data from "+intended_page)                  
            crawlled_page = self.opener.open(intended_page).read()
            moviePage = MoviePage(crawlled_page)
            

            print("Inserting Data into database....")
            for (i,movie) in enumerate(moviePage.getMovies()):

                self.movie_storage.insert_info(movie.getChineseTitle(),
                    movie.getEnglishTitle(),
                    movie.getUrl(),
                    movie.getDebut(),
                    movie.getWatchedDate(),
                    movie.getComment())


            if moviePage.hasNextPage:
                intended_page = moviePage.nextPage
            else:
                break

        print("Data crawling completed.")

        
        self.movie_storage.commit()

    def show_storage(self):
        self.movie_storage.show_storage()

    def done(self):
        self.movie_storage.close()


        
class movieStorage:
    def __init__(self):
        try:
            self.con = mdb.connect(host='localhost', user='root', passwd='1260', db='douban',charset='utf8')
            self.cur = self.con.cursor()

            self.cur.execute("DROP TABLE IF EXISTS movie_info")
            self.cur.execute('create table movie_info (id INT primary key AUTO_INCREMENT, \
                chineseTitle varchar(50),\
                englishTitle varchar(50),\
                url varchar(50),\
                debut varchar(50),\
                watchedDate varchar(20),\
                comment varchar(1000)\
                )')

            print("Datebase Created.")
        except mdb.Error, e:
            print(e)

            sys.exit(1)

    def insert_info(self,chineseTitle,englishTitle,url,debut,watchedDate,comment):
        #Insert movie information into database
        self.cur.execute('insert into movie_info (chineseTitle,englishTitle,url,debut,watchedDate,comment) \
            values (%s, %s, %s, %s, %s, %s)', [chineseTitle, englishTitle, url, debut, watchedDate, comment])



    def show_storage(self):
        #Show all the content in the database
        self.cur.execute("select * from movie_info")
        rows = self.cur.fetchall()

        for row in rows:
            print row

    def commit(self):
        self.con.commit()
    def close(self):
        self.cur.close()
        self.con.close()
        print("Database closed.")
       
if __name__ == '__main__':

    #Provide your email and password for Douban.com
    user_email=raw_input("Input Your Email: ")
    user_password=raw_input("Input Your Password: ")

    dm = DoubanMovies(email=user_email,password=user_password)
    dm.getMovieInfo()
    # dm.show_storage()
    dm.done()

