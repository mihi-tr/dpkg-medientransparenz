#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import csv
import itertools
import re
import nomenklatura

nkey=None
url="https://www.rtr.at/de/m/veroeffentl_medkftg_daten/Veroeffentlichung_3Abs3MedKFTG_Q3_2012.csv"

class NKCache():
  def __init__(self):
    self.ds=nomenklatura.Dataset("medientransparenz",api_key=nkey)
    self.links()

  def links(self):
    lnks=self.ds.links()
    self.cache=dict(((l.key,l.value["value"]) for l in
    itertools.ifilter(lambda x: x.value,lnks)))

  def lookup(self,key):
    if key in self.cache.keys():
      return self.cache[key]
    else:
      try:
        v=self.ds.lookup(key)
        return unicode(v)
      except self.ds.NoMatch:
        return None


    
def get(url):
  f = urllib2.urlopen(url)
  return csv.DictReader(f,delimiter=";")

def ukgen():
  """ Generates id's for rows in the csv"""
  n=0
  while True:
    n+=1
    yield n


def id(entry):
  entry["id"]=gen.next()
  return entry

def split_year(entry):
  entry["year"]=int(re.search("^([0-9]{4})",entry["QUARTAL"]).group(1))
  return entry

def clear_amount(entry):
  entry["EURO"]=float(entry["EURO"].replace(",","."))
  return entry

def bekanntgabe(entry):
  if entry["BEKANNTGABE"]=="2":
    d=u"Werbeaufträge und Medienkooperationen"
  else:
    d=u"Förderungen"
  entry["bekanntgabe_description"]=d
  return entry

def utf(entry):
  for (k,v) in entry.items(): 
    if type(v)==str:
      entry[k]=unicode(v,"iso-8859-1")
  return entry

def lookup(entry):
  r=cache.lookup(entry["MEDIUM_MEDIENINHABER"])
  if r:
    entry["medium"]=r
  else:
    entry["medium"]=entry["MEDIUM_MEDIENINHABER"]

  return entry

if __name__=="__main__":
  gen=ukgen()
  cache=NKCache()
  ignore=re.compile(" 31")
  fs=[id,clear_amount,split_year,bekanntgabe,utf,lookup]

  entries=itertools.ifilter(lambda x: x["LEERMELDUNG"]=="0", get(url))
  entries=itertools.ifilter(lambda x: not
  ignore.search(x["MEDIUM_MEDIENINHABER"]), entries)
  entries=reduce(lambda x,y: map(y,x),fs,entries)

  f=open("../data/mtg.csv","wb")
  keys=entries[0].keys()
  w=csv.writer(f)
  w.writerow([i.decode("iso-8859-1").encode("utf-8") for i in keys])
  for e in entries:
    row=[unicode(e[x]).encode("utf-8") for x in keys]
    w.writerow([unicode(e[x]).encode("utf-8") for x in keys])
  f.close()
