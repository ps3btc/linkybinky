#!/usr/bin/env python
#
# Copyright 2009 Hareesh Nagarajan

from django.utils import simplejson
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import mail
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.db import djangoforms

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

TWITGOO_QUERY='twitgoo'
TWITGOO_ADS = [
    'embed your tweet inside the image you upload http://twimgr.com',
    '140 characters; upload your image to a url of your choice http://twimgr.com',
    'twitter rewards brevity http://twimgr.com',
    'tweet inside an image url? http://twimgr.com',
    '1 love. brevity. be terse. upload image to a url of your choice http://twimgr.com',
    'login with gmail. upload image to a url of your choosing http://twimgr.com',
]

TWITPIC_QUERY='twitpic'
TWITPIC_ADS = TWITGOO_ADS

CANCER_QUERY='cancer'
CANCER_ADS = [
    'find people tweeting the word cancer with spam removed http://ps3btc.com/cancer',
    'find real time updates by people on cancer. spam removed. http://ps3btc.com/cancer',
    'cancer can be hard. fellow cancer tweets with spam removed http://ps3btc.com/cancer',
    'no spam. all tweets with the word cancer. fight it with friends http://ps3btc.com/cancer',
    'online, realtime cancer twitter support in 1 place. no spam. http://ps3btc.com/cancer',
]

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

OMG_QUERY='omg'
OMG_ADS = [
    'everyone saying omg right not http://ps3btc.com/omg',
    'i said omg once and i got hit by a car http://ps3btc.com/omg',
    'does god exist? who knows. http://ps3btc.com/omg',
    'i hate getting hit by a bus http://ps3btc.com/omg',
    'omg omg omg, so many people saying it all the time http://ps3btc.com/omg',
    'i wrote all the people saying omg RIGHT NOW http://ps3btc.com/omg',
    'silly stuff. everyong saying OMG http://ps3btc.com/omg',
]

FUCK_QUERY='fuck'
FUCK_ADS = [
    'everyone saying fuck right not http://ps3btc.com/fuck',
    'i said fcuk once and i got hit by a car http://ps3btc.com/fuck',
    'does god exist? who knows. http://ps3btc.com/fuck',
    'i hate getting hit by a bus http://ps3btc.com/fuck',
    'omg omg omg, so many people saying it all the time http://ps3btc.com/fuck',
    'i wrote all the people saying fcuk RIGHT NOW http://ps3btc.com/fuck',
    'silly stuff. everyong saying fcuk http://ps3btc.com/fuck',
    'who is tweeting the word fuck? http://ps3btc.com/fuck',
]

WTF_QUERY='wtf'
WTF_ADS = [
    'everyone saying wtf right not http://ps3btc.com/wtf',
    'i said wtf once and i got hit by a car http://ps3btc.com/wtf',
    'does god exist? who knows. http://ps3btc.com/wtf',
    'i hate getting hit by a bus http://ps3btc.com/wtf',
    'wtf wtf wtf, so many people saying it all the time http://ps3btc.com/wtf',
    'i wrote all the people saying wtf RIGHT NOW http://ps3btc.com/wtf',
    'silly stuff. everyong saying wtf http://ps3btc.com/wtf',
    'who is tweeting the word wtf? http://ps3btc.com/wtf',
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
    stack_trace = s.getvalue()
    logging.info('Oops: %s', stack_trace)
    send_mail(user, query, stack_trace)
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

def send_mail(user, query, stack_trace):
  logging.error('problem account account: %s query %s', user, query)
  mail.send_mail(sender="hareesh.nagarajan@gmail.com",
                 to="hxn <hareesh.nagarajan@gmail.com>",
                 subject="linkybinky ERROR %s %s" % (user, query),
                 body=stack_trace)

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
      elif query == OMG_QUERY:
        post(first_user, second_user, api, OMG_ADS)
      elif query == FUCK_QUERY:
        post(first_user, second_user, api, FUCK_ADS)
      elif query == WTF_QUERY:
        post(first_user, second_user, api, WTF_ADS)
      elif query == TWITPIC_QUERY:
        post(first_user, second_user, api, TWITPIC_ADS)
      elif query == TWITGOO_QUERY:
        post(first_user, second_user, api, TWITGOO_ADS)
      elif query == CANCER_QUERY:
        post(first_user, second_user, api, CANCER_ADS)
      else:
        logging.error('no users returned')
  except Exception, e:
      s = StringIO.StringIO()
      traceback.print_exc(file=s)
      logging.info('Oops: %s', s.getvalue())        

def wrap_cron():
  #do_cron('nwhat187', 'x167hd8w', NIGGA_QUERY)
  # THANKS ASSHOLE FOR STEALING MY PASSWORD!!
  do_cron('smithlakesha76', 'x167hd8w', NIGGA_QUERY)
  #do_cron('salasinps3', 'rala123', FUCK_QUERY)
  #do_cron('xalasinps3', 'rala123', WTF_QUERY)
  #do_cron('twotgr2', 'rala123', TWITGOO_QUERY)
  #do_cron('ralasinps3', 'rala123', OMG_QUERY)
  #do_cron('onetgr1', 'rala123', TWITPIC_QUERY)
  #do_cron('onecnr1', 'rala123', CANCER_QUERY)
  #do_cron('twocnr1', 'rala123', CANCER_QUERY)

class Home(webapp.RequestHandler):
  def get(self):
    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, {}))


class Cron(webapp.RequestHandler):
  def get(self):
    wrap_cron()
    self.response.out.write('done running cron')


##### CODED IN THE PLANE
class TwitterAccount(db.Model):
  username = db.StringProperty()
  password = db.StringProperty()
  entry_time = db.DateTimeProperty(auto_now_add=True)
  added_by = db.UserProperty()
  active = db.BooleanProperty(default=True)

class AccountsPage(webapp.RequestHandler):
  def get(self):
    query = db.GqlQuery("SELECT * FROM TwitterAccount ORDER BY added_by")
    for item in query:
      self.response.out.write("%s, %s, (%s)<br>" %
                             (item.username, item.password, item.added_by))

class TwitterAccountForm(djangoforms.ModelForm):
  class Meta:
    model = TwitterAccount
    exclude = ['active',
               'added_by']

class AddAccount(webapp.RequestHandler):
  def get(self):
    self.response.out.write('<html><body>'
                            '<form method="POST" '
                            'action="/add">'
                            '<table>')
    self.response.out.write(TwitterAccountForm())
    self.response.out.write('</table>'
                            '<input type="submit">'
                            '</form></body></html>')

  def post(self):
    data = TwitterAccountForm(data=self.request.POST)
    if data.is_valid():
      # Save the data, and redirect to the view page
      entity = data.save(commit=False)
      entity.added_by = users.get_current_user()
      entity.put()
      self.redirect('/accounts.html')
    else:
      # Reprint the form
      self.response.out.write('<html><body>'
                              '<form method="POST" '
                              'action="/add">'
                              '<table>')
      self.response.out.write(data)
      self.response.out.write('</table>'
                              '<input type="submit">'
                              '</form></body></html>')


class EditAccount(webapp.RequestHandler):
  def get(self):
    id = int(self.request.get('id'))
    item = TwitterAccount.get(db.Key.from_path('TwitterAccount', id))
    self.response.out.write('<html><body>'
                            '<form method="POST" '
                            'action="/edit">'
                            '<table>')
    self.response.out.write(TwitterAccountForm(instance=item))
    self.response.out.write('</table>'
                            '<input type="hidden" name="_id" value="%s">'
                            '<input type="submit">'
                            '</form></body></html>' % id)

  def post(self):
    id = int(self.request.get('_id'))
    item = Item.get(db.Key.from_path('TwitterAccount', id))
    data = TwitterAccountForm(data=self.request.POST, instance=item)
    if data.is_valid():
        # Save the data, and redirect to the view page
        entity = data.save(commit=False)
        entity.added_by = users.get_current_user()
        entity.put()
        self.redirect('/accounts.html')
    else:
        # Reprint the form
        self.response.out.write('<html><body>'
                                '<form method="POST" '
                                'action="/edit">'
                                '<table>')
        self.response.out.write(data)
        self.response.out.write('</table>'
                                '<input type="hidden" name="_id" value="%s">'
                                '<input type="submit">'
                                '</form></body></html>' % id)


#####


def main():
  wsgiref.handlers.CGIHandler().run(webapp.WSGIApplication([
      ('/', Home),
      ('/cron', Cron),
      #('/add', AddAccount),
      #('/edit', EditAccount),
      #('/accounts.html', AccountsPage),
      ]))

   
if __name__ == '__main__':
  main()
