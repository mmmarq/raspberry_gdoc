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
import gdata.spreadsheet.service
import gdata.service
import atom.service
import gdata.spreadsheet
import atom
import getopt
import sys
import string
import os
import shutil


class SimpleCRUD:

  def __init__(self, cf):
    if not os.path.isfile(cf):
      sys.exit(2)

    self.gd_client = gdata.spreadsheet.service.SpreadsheetsService()

    with open(cf) as f:
      for line in f:
        confdata = line.rstrip().split('=')
        if len(confdata) != 2:
          continue
        if confdata[0] == "email":
          self.gd_client.email = confdata[1]
        elif confdata[0] == "password":
          self.gd_client.password = confdata[1]
        elif confdata[0] == "curr_key":
          self.curr_key = confdata[1]

    if self.gd_client.email == "" or self.gd_client.password == "" or self.curr_key == "":
      print "Configuration file missing information!"
      sys.exit(2)
    self.gd_client.source = 'br.com.mmarq spreadsheet updater'
    self.gd_client.ProgrammaticLogin()
    self.list_feed = None
    self.inputFile = "/media/2/log/local_data.log"
    self.errorFile = "/media/2/log/error_local_data.log"
    # Retrieve worksheet id
    feed = self.gd_client.GetWorksheetsFeed(self.curr_key)
    id_parts = feed.entry[2].id.text.split('/')
    self.curr_wksht_id = id_parts[len(id_parts) - 1]
    
  def _ListInsertAction(self, row_data):
    try:
      entry = self.gd_client.InsertRow(self._StringToDictionary(row_data), 
          self.curr_key, self.curr_wksht_id)
      if isinstance(entry, gdata.spreadsheet.SpreadsheetsList):
        return True
      else:
        return False
    except:
      return False

  def _StringToDictionary(self, row_data):
    dict = {}
    for param in row_data.split():
      temp = param.split('=')
      dict[temp[0]] = temp[1]
    return dict
  
  def Run(self):
    if os.path.isfile(self.errorFile):
      os.remove(self.errorFile)
    e = open(self.errorFile, 'w')
    
    with open(self.inputFile) as f:
      for line in f:
        rawdata = line.split(',')
        if len(rawdata) == 6:
          data = "ano=" + rawdata[0] + " mes=" + rawdata[1] + " dia=" + rawdata[2] + " hora=" + rawdata[3] + " temperatura=" + rawdata[4] + " umidaderelativadoar=" + rawdata[5]
          #print data
          if not self._ListInsertAction(data):
            e.write(line)
      e.close()
      os.remove(self.inputFile)
      shutil.copy (self.errorFile,self.inputFile)
      os.remove(self.errorFile)


def main():
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
        
  sample = SimpleCRUD(cf)
  sample.Run()


if __name__ == '__main__':
  main()
