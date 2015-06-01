#!/usr/bin/python

try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
import getopt
import sys
import string
import os
import shutil

# Do OAuth2 stuff to create credentials object
import httplib2
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run

# Use it within gdata
import gdata.spreadsheet.service
import gdata.gauth

# get application credentials from google
def getGdataCredentials(client_secrets="client_secrets.json", storedCreds="creds.dat", scope=["https://spreadsheets.google.com/feeds"], force=False):
  storage = Storage(storedCreds)
  credentials = storage.get()
  if credentials is None or credentials.invalid or force:
    credentials = run(flow_from_clientsecrets(client_secrets, scope=scope), storage)
  if credentials.access_token_expired:
    credentials.refresh(httplib2.Http())
  return credentials

# get authorized spreadsheet client
def getAuthorizedSpreadsheetClient(client_secrets="client_secrets.json", storedCreds="creds.dat", force=False):
  credentials = getGdataCredentials(client_secrets=client_secrets, storedCreds=storedCreds, scope=["https://spreadsheets.google.com/feeds"], force = force)
  client = gdata.spreadsheet.service.SpreadsheetsService(
    additional_headers={'Authorization' : 'Bearer %s' % credentials.access_token})
  return client

def main():
  global credential_data
  global json_cred
  global spreadsheet_key
  global worksheet_key
  global input_file
  global error_file
  
  # parse command line options
  try:
    opts, args = getopt.getopt(sys.argv[1:], "c:j:", ["cf=","jf="])
  except getopt.error, msg:
    print 'python update_spreadsheet.py --cf [creds_file] --jf [json_secrets_file]'
    sys.exit(2)
  
  cf = ''
  jf = ''
  # Process options
  for o, a in opts:
    if o == "--cf":
      cf = a
    if o == "--jf":
      jf = a

  if cf == '':
    print 'python update_spreadsheet.py --cf [creds_file] --jf [json_secrets_file]'
    sys.exit(2)

  if jf == '':
    print 'python update_spreadsheet.py --cf [creds_file] --jf [json_secrets_file]'
    sys.exit(2)

  print 'Client secrets file: ' + jf
  print 'Credentials file: ' + cf

  # google authentication
  storage = Storage(cf)
  credentials = storage.get()
  if credentials is None or credentials.invalid:
    credentials = run(flow_from_clientsecrets(jf, scope=["https://spreadsheets.google.com/feeds"]), storage)

  # get authorized client
  #gd_client = getAuthorizedSpreadsheetClient(json_cred,credential_data)

if __name__ == '__main__':
  main()

