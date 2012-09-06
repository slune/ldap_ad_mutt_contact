#!/usr/bin/env python

import sys
import ldap
import pickle
from optparse import OptionParser

class Search():

  def search(self, search_by):

    # try local search first
    results = self.local_search(search_by)
    if results==[]:
      self.ldap_init()
      results = self.ldap_search(search_by)
    return results

  def load_local_data(self, dump_file):

    try:
      fd = open(dump_file, 'rb')
      old_data = pickle.load(fd)
      fd.close()
    except IOError:
      return {}

    return old_data

  # search local file
  def local_search(self, search_by):

    try:
      return self.old_data[search_by]
    except KeyError:
      return []
  
  # search ldap file
  def ldap_search(self, search_by):

    # search ldap
    resID = self.lconn.search(self.search_conf['base'], ldap.SCOPE_SUBTREE, search_by)

    data = []
    # walk through data and create structure with resukts
    while 1:
      rt,rd=self.lconn.result(resID, 0)
      if rd == []:
        break
      if rt == ldap.RES_SEARCH_ENTRY:
        data.append(rd[0][1])

    fd = open(self.dump_file, 'wb')
    self.old_data[search_by]=data
    stats = pickle.dump(self.old_data, fd)
    fd.close()

    return data

  def ldap_init(self):
    self.lconn = ldap.initialize(self.search_conf['server'])
    self.lconn.protocol_version = 3
    self.lconn.set_option(ldap.OPT_REFERRALS, 0)
    self.lconn.simple_bind_s(self.search_conf['user'], self.search_conf['password'])

  def __init__(self, search_conf, dump_file):
    self.search_conf=search_conf
    self.dump_file=dump_file
    self.old_data = self.load_local_data(self.dump_file)

def show_mutt(data):
  show_data = ""
  print 
  default_keys_mut = ['mail', 'displayName', 'telephoneNumber', 'mobile']
  for key in default_keys_mut:
    try:
      show_data += str(data[key][0]) + "\t"
    except:
      show_data += "None" + "\t"
      if key == "mail":
        return

  print show_data

def show_terminal(data):
  print 40*"*"
  default_keys_ter = ['displayName', 'userPrincipalName', 'mail', 'manager', 'department', 'telephoneNumber', 'mobile', ""]
  for key in default_keys_ter:
    try:
      dato = data[key][0]
    except:
      dato = "None"

    print ("%18s: %s")%(key, dato)

def show_all(data):
  for item in data:
    print item, data[item]
    print 50*"*"


def main():
  parser = OptionParser()
  parser.add_option("-n", "--name", action='store', type='string', dest='name', help="find by username", default="")
  parser.add_option("-m", "--mobile", action='store', type='string', dest='mobile', help="find by mobile", default="")
  parser.add_option("-s", "--show", action='store', type='string', dest='show', help="type of output", default="terminal")

  (options, args) = parser.parse_args()

  if options.mobile:
    search_by = "mobile=*%s*" % options.mobile
  elif options.name:
    search_by = "sAMAccountName=*%s*" % options.name

  search_conf = {
    'user':             "user",
    'base':             "DC=xxx,DC=xxx",
    'server':           "ldap://ldap.xxx.xxx:1234",
    'password':         "xxxxxxx",
  }

  dump_file="/home/slune/.mutt/ldap_cache.pkl"

  srch_cls = Search(search_conf, dump_file)
  res = srch_cls.search(search_by)

  for dato in res:
    if options.show=="terminal":
      show_terminal(dato)
    elif options.show=="mutt":
      show_mutt(dato)

if __name__ == "__main__":
  sys.exit(main())

