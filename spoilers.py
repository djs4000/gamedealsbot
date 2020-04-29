import sqlite3
import time
import praw
import prawcore
import requests
import logging
import Config
from bs4 import BeautifulSoup
responded = 0
footer = ""
reddit = praw.Reddit(client_id=Config.cid,
                     client_secret=Config.secret,
                     password=Config.password,
                     user_agent=Config.agent,
                     username=Config.user)
subreddit = reddit.subreddit(Config.subreddit)

apppath='/home/reddit/gamedealsbot/'

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=apppath+'spoiler_monitor.log',
                    filemode='a')

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

con = sqlite3.connect(apppath+'gamedealsbot.db')

logging.info("scanning spoiler...")

while True:
  for submission in subreddit.new(limit=50):
    if submission.spoiler and submission.link_flair_text != "Expired":
      if submission.link_flair_text is not None:
        flairtime = str( int(time.time()))
        cursorObj = con.cursor()
        cursorObj.execute('INSERT INTO flairs(postid, flairtext, timeset) VALUES("'+submission.id+'","'+submission.link_flair_text+'",' + flairtime + ')')
        con.commit()
      submission.mod.flair(text='Expired', css_class='expired')
      logging.info("flairing spoiled post of " + submission.title);
    if not submission.spoiler and submission.link_flair_text == "Expired":
      submission.mod.flair(text='', css_class='')
      logging.info("unflairing spoiled post of " + submission.title)
      cursorObj = con.cursor()
      cursorObj.execute('SELECT * FROM flairs WHERE postid = "'+submission.id+'"')
      rows = cursorObj.fetchall()
      if len(rows) is not 0:
        cursorObj.execute('DELETE FROM flairs WHERE postid = "'+submission.id+'"')
        submission.mod.flair(text=rows[0][2], css_class='')

  time.sleep(30)