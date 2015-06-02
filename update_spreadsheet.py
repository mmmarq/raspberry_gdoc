#!/usr/bin/python
#
# Copyright (C) 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Based on script created by api.laurabeth@gmail.com (Laura Beth Lincoln)
__author__ = 'marcelo.martim@gmail.com (Marcelo Martim Marques)'


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

def stringToDictionary(raw_data):
  rowData = {}
  for param in raw_data.split():
    temp = param.split('=')
    rowData[temp[0]] = temp[1]
  return rowData

def main():
  credential_data = ''
  json_cred = ''
  spreadsheet_id = ''
  worksheet_id = ''
  input_file = ''
  error_file = ''
  
  # parse command line options
  try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["cf="])
  except getopt.error, msg:
    print 'python update_spreadsheet.py --cf [configuration_file]'
    sys.exit(2)
  
  cf = ''
  # Process options
  for o, a in opts:
    if o == "--cf":
      cf = a

  if cf == '':
    print 'python update_spreadsheet.py --cf [configuration_file]'
    sys.exit(2)

  with open(cf) as f:
    for line in f:
      confdata = line.rstrip().split('=')
      if len(confdata) != 2:
        continue
      if confdata[0] == "credential_data":
        credential_data = confdata[1]
      elif confdata[0] == "json_cred":
        json_cred = confdata[1]
      elif confdata[0] == "spreadsheet_id":
        spreadsheet_id = confdata[1]
      elif confdata[0] == "worksheet_id":
        worksheet_id = confdata[1]
      elif confdata[0] == "input_file":
        input_file = confdata[1]
      elif confdata[0] == "error_file":
        error_file = confdata[1]

  # check configuration data
  if (credential_data == '') or (json_cred == '') or (spreadsheet_id == '') or (worksheet_id == '') or (input_file == '') or (error_file == ''):
    print 'Unable to read all required values from configuration file'
    sys.exit(2)

  # google authentication
  storage = Storage(credential_data)
  credentials = storage.get()
  if credentials is None or credentials.invalid:
    credentials = run(flow_from_clientsecrets(json_cred, "https://spreadsheets.google.com/feeds"), storage)

  # get authorized client
  gd_client = getAuthorizedSpreadsheetClient(json_cred,credential_data)

  if os.path.isfile(error_file):
    os.remove(error_file)
  e = open(error_file, 'w')
  
  with open(input_file) as f:
    for line in f:
      rawdata = line.split(',')
      if len(rawdata) == 6:
        rowData = stringToDictionary("ano=" + rawdata[0] + " mes=" + rawdata[1] + " dia=" + rawdata[2] + " hora=" + rawdata[3] + " temperatura=" + rawdata[4] + " umidaderelativadoar=" + rawdata[5])
        entry = gd_client.InsertRow(rowData, spreadsheet_id, worksheet_id)

        if not isinstance(entry, gdata.spreadsheet.SpreadsheetsList):
          e.write(line)

    e.close()
    os.remove(input_file)
    shutil.copy (error_file,input_file)
    os.remove(error_file)

if __name__ == '__main__':
  main()
