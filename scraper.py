"""
Scott Vincent
Web Crawler - Email Scrapping Tool
Feb 2015
"""
#!/usr/bin/python

import sys
import re
import urllib2
import os
import argparse
from bs4 import BeautifulSoup

#Functions
"""
addEmail(string) - checks to see if the email already exists in the current list of emails
If it does then it will not add it
If it does not, then it will add it to the list
"""
def addEmail(email, emailListi, verbose, currentNumEmails):
    i=0
    email = email.lower()
    
    #make sure current email in que does not exist in the current list of emails
    with open(emailList, 'r') as searchfile:
        for line in searchfile:
            if email in line: 
                i += 1
    if i == 0:
        out = open(emailList,'a')
        out.write(email+"\n")
        out.close()
        currentNumEmails += 1
        if verbose == True:
            print "Email found: %s" %(email)
    return currentNumEmails

def addURL(url, domain):

    if domain in url:
        if url in urlList:
            pass
        else:
            urlList.append(url)        


#Gives you the location of the nth iteration(0=first iteration)
def findnth(string, sub, n):
    parts= string.split(sub, n+1)
    if len(parts)<=n+1:
        return -1
    return len(string)-len(parts[-1])-len(sub)


#Validate Args
parser = argparse.ArgumentParser(description="How to use this scraper...")
parser.add_argument("-s", "--site",  action="store", dest="site", help="The first site you would like to scrape", required=True)
parser.add_argument("-l", "--limit",  action="store", dest="lim", type=int, help="The number of emails you would like to scrape")
parser.add_argument("-v", "--verbose", action="store_true", dest="verbose",  help="Verbose Mode")
parser.add_argument("-ef", "--emailFile", action="store", dest="el", default="emails", help="File you would like to store the emails")
parser.add_argument("-uf", "--URLFile", action="store", dest="urls", default="urls", help="File you would like to store the URLs used")
args = parser.parse_args()

#declare variables
site = args.site
numEmails = args.lim
verbose = args.verbose
emailList = args.el
urls = args.urls
currentNumEmails = 0

make = open(emailList,'w')
make.close()
make = open(urls,'w')
make.close()

urlList=[]

#make sure url includes http
if not site.startswith('http'):
    site = "http://" + site

#obtain only the domain name
start = findnth(site, "/", 1)
end = findnth(site, "/", 2)
if end == -1:
    domain = site[start+1:]
else:
    domain = site[start+1:end]

if domain.startswith("w"):
    dot = domain.find(".")
    domain = domain[dot+1:]
domain = domain.rstrip()

#Add site to list of urls
addURL(site, domain)


for site in urlList:
    
    #make sure url includes http
    if not site.startswith('http'):
        site = "http://" + site

    if verbose == True:
        print site

    #Get a pages code and put in a file
    try:
        response = urllib2.urlopen(site)
        html = response.read()
        response.close()
        out = open('page.out','w')
        out.write(html)
        out.close()
    except urllib2.HTTPError, err:
        if err.code == 404:
            if verbose == True:
                print site
                print "Error 404 - page not found :("
        elif err.code == 403:
            if verbose == True:
                print site
                print "Error 403 - Access denied :'("
        else:
            if verbose == True:
                print site
                print "Some other HTTP error :( ", err.reason
    except urllib2.URLError, err:
        if urllib2.URLError == 1:
            if verbose == True:
                "Error number 1 occured \n"
        else:
            if verbose == True:
                print "Some  URL error happened :( ", err.reason
            if len(urlList) == 1:
                print "Link provided did not work. Try again with another link."
                sys.exit()
    
    #Go through that page to find emails
    pattern = re.compile("[-0-9a-zA-Z.+_]+@[-0-9a-zA-Z.+_]+\.[a-zA-Z]{2,4}")
    for i, line in enumerate(open('page.out')):
            for match in re.findall(pattern, line):
                currentNumEmails = addEmail(match, emailList, verbose, currentNumEmails)    
                if currentNumEmails == numEmails:
                    print "%i Emails have been found. Emails have been written to %s." %(currentNumEmails, emailList)
                    break
   
    if currentNumEmails == numEmails:
        break

    #Create beautiful soup object to parse a tags
    #soup = BeautifulSoup([html], "html.parser")
    soup = BeautifulSoup(html)

    #parsing all a tags to create full useable links
    for link in soup.find_all('a'):
        uni = unicode(link)
        utf8string = uni.encode("utf-8")
        x = utf8string.find('href')
        href = utf8string[x:]
        firstQuote = findnth(href, '"', 0)
        secondQuote = findnth(href, '"', 1)
        fullLink = href[firstQuote+1:secondQuote]
        if fullLink.startswith("/"):
            url = domain + fullLink
            addURL(url, domain)
        elif fullLink.startswith("http"):
            url = fullLink
            addURL(url, domain)

#Wirte All of the URLs found to urls
out = open(urls,'w')
for i in urlList:
    out.write(i+"\n")
out.close()

#count lines of a file
with open(emailList) as f:
    print "Number of emails: " 
    print sum(1 for _ in f)

with open(urls) as f:
    print "Number of Links: " 
    print sum(1 for _ in f)

