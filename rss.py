#!/usr/bin/env python
import feedparser, os, time, re, signal, sys, string
import subprocess as sub

# For interruption handling
def signal_handler(signal, frame):
        print "Saving progress..."
        
        print "Exiting"
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


feeds = {}
authors = {}
categories = {}

# defines wich feature is used to send notifications
# growl should be implemented
notify_send = True

#class Category:
        
# Author, wich contains feed entries
class Author:
    def __init__(self, name, score=0):
        self.name = name
        self.score = score
        self.items = {}

    def increaseScore(self,score=1):
        self.score += score

    def decreaseScore(self,score=1):
        self.score -= score

    def addItem(self,item):
        if item.title not in self.items:
            self.items[item.title] = item
            return True
        return False

    def addItems(self,items):
        added = False
        for item in items:
            if addItems(item):
                added = True
        return added

    def removeItem(self,item):
        if item.title in self.items:
            del self.items[item.title]
            return True
        return False

# Feed, wich contains feed entries (items)
class Feed:
    def __init__(self, url):
        feed = feedparser.parse(url)

        self.items = {}
        
        if feed["bozo"] == 1:
            raise TypeError("The URL is not an RSS-feed")
            
        self.url = url
        self.title = fixAscii(feed["channel"]["title"])
        
        for i in feed["items"]:
            item = Item(i)
            if item.title not in self.items.keys():
                self.items[item.title] = item
                                               
    def __getitem__(self, n):
        if (n - 1) > len(self.items):
            return None
        
        return self.items[n]
        
    def __len__(self):
        return len(self.items)
        
    def __str__(self):
        return self.title
        
    def read(self):
        self.red = True

# An item wich correspond to and entry in a feed
class Item:
    def __init__(self, item):
        self.title = fixAscii(item["title"])
        self.site = re.search('.+www\.(.+)\..+/.+', item["link"].lower()).group(1)
        self.refers = {}
        
        if "author" in item:
            self.author = fixAscii(item["author"])
        else:
            self.author = self.site
            
        if self.author in authors:
            self.author = authors[self.author]
        else:
            authors[self.author] = Author(self.author)
            self.author = authors[self.author]
            
        self.link = item["link"]
        self.published = item["published"]
        
        self.seen = False
        self.timeSeen = None
        
        for x in authors:
            if x != self.author.name:
                if x in str(item):
                    if x in self.refers:
                        self.refers[x] += 1
                    else:
                        self.refers[x] = 1
        
    def __str__(self):
        return "%s - %s" % (self.author.name, self.title)
        

# Reed feed from a given file with feed URLs
def readFeedsFromFile(filename):
    f = open(filename, 'r').readlines()
    for feed in f:
        addFeed(feed.strip('\n'))

        
# A quick fix for items that contains non-ascii characters
def fixAscii(s):
    return "".join(x if ord(x) < 128 else '?' for x in s)  
    
# Create feed objects from URLs
def addFeed(url):
    try:
        feed = Feed(url)
    except TypeError:
        print "Error creating feed"
        return False
    
    if feed.title not in feeds:
        feeds[feed.title] = feed
        return True
    
    return False

# Send notification to the user
def sendNotification(text, length=5):
    filtered = string.replace(str(text), "'", "")
    length = length * 1000
    
    if notify_send:
        notifySend(filtered, length)

# Standard linux notification, to be swiched out for Growl
def notifySend(text, length):
    os.system("notify-send -t %i '%s'" % (length, text))

# Run loop
def run(interval=10):
    readFeedsFromFile("rss.txt")
    #while True:
        #time.sleep(interval)
        
    for feed in feeds.values():
        for item in feed.items.values():
            for x in item.refers:
                print "%s -> %s" % (item.author.name, x)
            sendNotification(item,1)
            time.sleep(1)
        
        #poll data
        #check if unread/new
        #give valid notification


run()
