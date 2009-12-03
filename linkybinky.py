#!/usr/bin/env python
#
# Copyright 2009 Hareesh Nagarajan

from django.utils import simplejson
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import mail

import StringIO
import logging
import os
import random
import sys
import time
import traceback
import twitter
import urllib2
import wsgiref.handlers

PS3_QUERY='ps3'
PS3_ADS = [
    'if you like ps3+twitter you might (low probability) like http://ps3btc.com #ps3btc :)',
    'i suck at the ps3. but i like ps3+twitter. thusly, i wrote http://ps3btc.com #ps3btc',
    'when i got fragged for the 18th time in #mw2, i wrote http://ps3btc.com #ps3btc',
    'life is just ok. ps3+twitter for ever. ergo, i wrote http://ps3btc.com #ps3btc',
    'find ps3 friends, who happen to be on twitter. so i wrote http://ps3btc.com #ps3btc',
    'i like cake. i like ps3. i like twitter. so i wrote http://ps3btc.com #ps3btc',
    'why do i get killed in #mw2 so quickly. find crappy ps3 players http://ps3btc.com #ps3btc',
    'is ps3 really better than cake? i think so. so i wrote http://ps3btc.com #ps3btc',
    'find out what people are saying about the ps3 on twitter. http://ps3btc.com #ps3btc',
    'public service annoucement. ps3+twitter addiction. http://ps3btc.com #ps3btc',
    'i ma shutup if you dont like the ps3. ps3+twitter addiction. http://ps3btc.com #ps3btc',
    'no friends. suck at gaming. atleast i can program. ps3+twitter love. http://ps3btc.com #ps3btc',
    '2 years later i still dont have a podium finish in mw2. ps3+twitter. http://ps3btc.com #ps3btc',
    'i only have 1 friend in PSN. i found him on http://ps3btc.com #ps3btc',
    'not many like a ps3+twitter website, maybe you do? http://ps3btc.com #ps3btc',
    'when i dont find a co-op on borderlands, i visit my ps3 website http://ps3btc.com #ps3btc',
    'funny ps3 tweets here. funny husband/wife comments. visit http://ps3btc.com #ps3btc',
    ]

XBOX_QUERY='xbox'
XBOX_ADS = [
    'if you like xbox+twitter you might (low probability) like http://ps3btc.com/xbox',
    'i suck at the xbox. but i like xbox+twitter. thusly, i wrote http://ps3btc.com/xbox',
    'when i got fragged for the 18th time in #odst, i wrote http://ps3btc.com/xbox',
    'life is just ok. xbox+twitter for ever. ergo, i wrote http://ps3btc.com/xbox',
    'find xbox friends, who happen to be on twitter. so i wrote http://ps3btc.com/xbox',
    'i like cake. i like xbox. i like twitter. so i wrote http://ps3btc.com/xbox',
    'why do i get killed in #odst so quickly. find crappy xbox players http://ps3btc.com/xbox',
    'is xbox really better than cake? i think so. so i wrote http://ps3btc.com/xbox',
    'find out what people are saying about the xbox on twitter. http://ps3btc.com/xbox',
    'public service annoucement. xbox+twitter addiction. http://ps3btc.com/xbox',
    'i ma shutup if you dont like the xbox. xbox+twitter addiction. http://ps3btc.com/xbox',
    'no friends. suck at gaming. atleast i can program. xbox+twitter love. http://ps3btc.com/xbox',
    '2 years later i still dont have a podium finish in halo. xbox+twitter. http://ps3btc.com/xbox',
    'i only have 1 friend in live. i found him on http://ps3btc.com/xbox',
    'not many like a xbox+twitter website, maybe you do? http://ps3btc.com/xbox',
    'when i dont find a co-op on odst, i visit http://ps3btc.com/xbox',
    'funny xbox tweets here. funny husband/wife comments. visit http://ps3btc.com/xbox',
    ]

WII_QUERY='wii'
WII_ADS = [
    'if you like wii+twitter you might (low probability) like http://ps3btc.com/wii',
    'i suck at the wii. but i like wii+twitter. thusly, i wrote http://ps3btc.com/wii',
    'when i got fragged for the 18th time in #odst, i wrote http://ps3btc.com/wii',
    'life is just ok. wii+twitter for ever. ergo, i wrote http://ps3btc.com/wii',
    'find wii friends, who happen to be on twitter. so i wrote http://ps3btc.com/wii',
    'i like cake. i like wii. i like twitter. so i wrote http://ps3btc.com/wii',
    'why do i get killed in #odst so quickly. find crappy wii players http://ps3btc.com/wii',
    'is wii really better than cake? i think so. so i wrote http://ps3btc.com/wii',
    'find out what people are saying about the wii on twitter. http://ps3btc.com/wii',
    'public service annoucement. wii+twitter addiction. http://ps3btc.com/wii',
    'i ma shutup if you dont like the wii. wii+twitter addiction. http://ps3btc.com/wii',
    'no friends. suck at gaming. atleast i can program. wii+twitter love. http://ps3btc.com/wii',
    '2 years later i still dont have a podium finish in halo. wii+twitter. http://ps3btc.com/wii',
    'i only have 1 friend in live. i found him on http://ps3btc.com/wii',
    'not many like a wii+twitter website, maybe you do? http://ps3btc.com/wii',
    'when i dont find a co-op on odst, i visit http://ps3btc.com/wii',
    'funny wii tweets here. funny husband/wife comments. visit http://ps3btc.com/wii',
    ]

NIGGA_QUERY='nigga'
NIGGA_ADS = [
    'grew up on the south side. love twitter. built this http://ps3btc.com/n #niggawhat :)',
    'you gonna love this boo http://ps3btc.com/n #niggawhat :)',
    'i ma shut up if you dont like http://ps3btc.com/n #niggawhat :)',
    'twitter love. nigga love. 1 page. http://ps3btc.com/n #niggawhat :)',
    'nigga wha? 1 page. all on twitter. http://ps3btc.com/n #niggawhat :)',
    'south side. 1 love. twitter love. http://ps3btc.com/n #niggawhat :)',
    'i ma crazy. sometimes. love twitter. http://ps3btc.com/n #niggawhat :)',
    'i guarantee you will love this. http://ps3btc.com/n #niggawhat ??! :)',
    'shakin my head. you gonn love this. http://ps3btc.com/n #niggawhat ??! :)',
    'friendship more important than money. friends here http://ps3btc.com/n #niggawhat :)',
    'he just didnt press me on twitter. LOL! friends here http://ps3btc.com/n #niggawhat :)',
    'he wear jordans. i dont. i like twitter. http://ps3btc.com/n #niggawhat :)',
    'looking to follow a brother or sista? love twitter? http://ps3btc.com/n #niggawhat :)',
    'you might not wear jordans. but i like twitter. http://ps3btc.com/n #niggawhat :)',
    'phoenix to atlanta to chicao. full circle? http://ps3btc.com/n #niggawhat :)',
    'life love or money. i go for friends. http://ps3btc.com/n #niggawhat :)',
    'my brother rapped his way through school. i was fat. http://ps3btc.com/n #niggawhat :)',
    'good looks havent been me. like twitter. http://ps3btc.com/n #niggawhat :)',
    'some say my tweets are random. but why. http://ps3btc.com/n #niggawhat :)',
    ]

def do_search(query):
  """Makes a get request fetching the JSON from twitter. If something
  is broken, we jam a 'something is broken' message into the HTML and
  return None. On success we return the dictionary of the search
  results."""
  
  # TODO(hareesh): remove the lang=en restricts
  url = 'http://search.twitter.com/search.json?q=%s&rpp=100' % query

  try:
    handle = urllib2.urlopen(url)
    data = simplejson.loads(handle.read())
    return data['results']
  except Exception, e:
    s = StringIO.StringIO()
    traceback.print_exc(file=s)
    logging.info('Oops: %s', s.getvalue())
    return None


def spam(source):
  """Takes as argument the source used to generate the tweet. Returns
  true (=spam)if the source belongs to the following sources such as
  RSS feeds, vanilla usage of the twitter API, etc. TODO(hareesh): In
  my opinion, I've seen a large percentage of of spammers and bots use
  this mechanism to tweet."""
    
  ignore_sources =  [ 'apiwiki.twitter.com',
                      'twitterfeed.com',
                      'rss2twitter.com',
                      'skygrid.com',
                      'assetize.com',
                      'Twitter Tools',
                      'wp-to-twitter',
                      'http://twitter.com',
                      'pivotallabs.com',
                      '/devices',
                      'bit.ly',
                      'allyourtweet.com'
                      'wordpress',
                      'alexking.org',
                      'bravenewcode.com',
                      ]

  for ign in ignore_sources:
    if source.find(ign) >= 0:
      return True

  return False  


def is_web_source(source):
  if source.find('http://twitter.com/') >= 0:
    return True


def filter_results(results):
  if not results:
    return []

  new_results = []
  no_spam_results = []
  for r in results:
    # To pick a user to send tweets to they must not be from spammy
    # sources and must not have a link inside the tweet
    lang = True
    if r.has_key('iso_language_code'):
      if r['iso_language_code'] != 'en':
        lang = False
    
    if not spam(r['source']):
      no_spam_results.append(r)
      if r['text'].find('http://') == -1 and lang:
        new_results.append(r)

  if len(new_results) < 4:
    if len(no_spam_results) < 4:
      logging.error('Did not filter anything returning results')
      return results
    else:
      logging.error('Did not filter much, returning no_spam_results')
      return no_spam_results

  return new_results


def post(first_user, second_user, api, ads):
  random_ad = int(random.uniform(0, len(ads)))
  tw = '@%s, @%s %s' % (first_user, second_user, ads[random_ad])
  if len(tw) > 140:
    logging.error('Too long tweet: %s (%d)', tw, len(tw))
    return -1
  
  logging.info(tw)
  status=api.PostUpdate(tw)
  return random_ad

def send_mail(user, query):
  mail.send_mail(sender="hareesh.nagarajan@gmail.com",
                 to="hxn <hnagar2@gmail.com>",
                 subject="problem! %s %s" % (user, query),
                 body="problem!")

def do_cron(user, pw, query):
  try:
    api = twitter.Api(username=user, password=pw)
    new_results = filter_results(do_search(query))
    if len(new_results) > 0:
      random_user_idx = int(random.uniform(0, len(new_results) - 1))
      first_user = new_results[random_user_idx]['from_user']
      next_idx = (random_user_idx + 1) % len(new_results)
      second_user = new_results[next_idx]['from_user']
      logging.info('picked @%s, @%s (query: %s, total %d)', first_user, second_user, query, len(new_results))
      if query == PS3_QUERY:
        post(first_user, second_user, api, PS3_ADS)
      elif query == WII_QUERY:
        post(first_user, second_user, api, WII_ADS)
      elif query == XBOX_QUERY:
        post(first_user, second_user, api, XBOX_ADS)
      elif query == NIGGA_QUERY:
        post(first_user, second_user, api, NIGGA_ADS)
      else:
        logging.error('no users returned')
  except:
    send_mail(user, query)

def wrap_cron():
  do_cron('nwhat187', 'x167hd8w', NIGGA_QUERY)
  do_cron('smithlakesha76', 'x167hd8w', NIGGA_QUERY)

class Home(webapp.RequestHandler):
  def get(self):
    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, {}))


class Cron(webapp.RequestHandler):
  def get(self):
    wrap_cron()
    self.response.out.write('done running cron')


def main():
  wsgiref.handlers.CGIHandler().run(webapp.WSGIApplication([
      ('/', Home),
      ('/cron', Cron),
      ]))

   
if __name__ == '__main__':
  main()
