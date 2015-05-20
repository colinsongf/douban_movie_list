# Basics
This is a self-entertaining project, in which the author wants to experiment on crawling data from Internet using python and storing the crawled content into MySQL.

The objective website is [Douban.com](www.douban.com), roughly speaking, the Chinese version of [IMDb](http://www.imdb.com/). In this website, users are allowed to give comments and ratings to the movies that they have watched. Those watched movies will be listed under the personal page of users.

The aim of this project is to crawl the information of those watched movies from the author's personal page and to store them in the database. The biggest difficulty is the authentication with identifying code, that is, to login, users are required to type in not only the username and password but also the identifying code from one distorted picture. This identifying code obviously requires human input and is not decodeable by programming codes.

To solve this issue, upon constructing the crawler, the picture of identifying code will be shown in the web-browser and the user of this project will be asked to type in the code in the command line. After that, the crawler is free to crawl any content from the account of the user.

The rest of this project follows a typical web-crawling paradigm: extracting relevant information by analyzing DOM of crawlled page using [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/bs4/doc/) and storing the extracted information to local MySQL database using [MySQL-python](https://pypi.python.org/pypi/MySQL-python). 

After all, this project is just for fun and practicing, which will not ensure the robustness of codes. The author perfectly understands a lot of improvement can be made to the existing project and suggestions are certainly welcome.    


# Functions
This project can do four things:

* Establish an authenticated crawler with identifying code.
* Crawl movies from the personal page of douban.
* Extract movie relevant information from downloaded pages.
* Store the extracted information to local database.
