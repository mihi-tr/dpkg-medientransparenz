#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import csv
import itertools
import re
import nomenklatura

nkey=None
url="https://www.rtr.at/de/m/veroeffentl_medkftg_daten/Veroeffentlichung_3Abs3MedKFTG_Q3_2012.csv"

def get(url):
  f = urllib2.urlopen(url)
  return csv.DictReader(f,delimiter=";")

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
  ds=nomenklatura.Dataset("medientransparenz",api_key=nkey)
  try:
    v=ds.lookup(entry["MEDIUM_MEDIENINHABER"])
    entry["MEDIUM_MEDIENINHABER"]=unicode(v)

  except ds.NoMatch:
    print u"no match for %s"%entry["MEDIUM_MEDIENINHABER"]
  return entry

fs=[clear_amount,split_year,bekanntgabe,utf,lookup]

entries=itertools.ifilter(lambda x: x["LEERMELDUNG"]=="0", get(url))
entries=reduce(lambda x,y: map(y,x),fs,entries)

f=open("../data/mtg.csv","wb")
keys=entries[0].keys()
w=csv.writer(f)
w.writerow([i.decode("iso-8859-1").encode("utf-8") for i in keys])
for e in entries:
  row=[unicode(e[x]).encode("utf-8") for x in keys]
  w.writerow([unicode(e[x]).encode("utf-8") for x in keys])
f.close()
