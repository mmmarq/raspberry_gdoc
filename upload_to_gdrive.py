#!/usr/bin/python
'''
Created on 6 Jun 2012

@author: Jeremy Blythe

Motion Uploader - uploads videos to Google Drive

Read the blog entry at http://jeremyblythe.blogspot.com for more information

GData library can be found at https://code.google.com/p/gdata-python-client/
'''

import smtplib
from datetime import datetime

import os.path
import getpass
import sys

import gdata.data
import gdata.docs.data
import gdata.docs.client
import ConfigParser

class FileUploader:
    def __init__(self, config_file_path):
        # Load config
        config = ConfigParser.ConfigParser()
        config.read(config_file_path)
        
        # GMail account credentials
        self.username = config.get('gmail', 'user')
        self.password = config.get('gmail', 'password')
        self.from_name = config.get('gmail', 'name')
        self.sender = config.get('gmail', 'sender')
        
        # Recipient email address (could be same as from_addr)
        self.recipient = config.get('gmail', 'recipient')        
        
        # Subject line for email
        self.subject = config.get('gmail', 'subject')
        
        # First line of email message
        self.message = config.get('gmail', 'message')
                
        # Folder (or collection) in Docs where you want the videos to go
        self.folder = config.get('docs', 'folder')
        
        # Options
        self.delete_after_upload = config.getboolean('options', 'delete-after-upload')
        self.send_email = config.getboolean('options', 'send-email')
        
        self._create_gdata_client()

    def _create_gdata_client(self):
        """Create a Documents List Client."""
        self.client = gdata.docs.client.DocsClient(source='file_uploader')
        self.client.http_client.debug = False
        self.client.client_login(self.username, self.password, service=self.client.auth_service, source=self.client.source)
               
    def _get_folder_resource(self):
        """Find and return the resource whose title matches the given folder."""
        col = None
        for resource in self.client.GetAllResources(uri='/feeds/default/private/full/-/folder'):
            if resource.title.text == self.folder:
                col = resource
                break    
        return col
    
    def _send_email(self,msg):
        '''Send an email using the GMail account.'''
        senddate=datetime.strftime(datetime.now(), '%Y-%m-%d')
        m="Date: %s\r\nFrom: %s <%s>\r\nTo: %s\r\nSubject: %s\r\nX-Mailer: My-Mail\r\n\r\n" % (senddate, self.from_name, self.sender, self.recipient, self.subject)
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(self.username, self.password)
        server.sendmail(self.sender, self.recipient, m+msg)
        server.quit()    

    def _upload(self, file_path, folder_resource):
        '''Upload the file and return the doc'''
        doc = gdata.docs.data.Resource(type='file', title=os.path.basename(file_path))
        media = gdata.data.MediaSource()
        media.SetFileHandle(file_path, 'application/octet-stream')
        doc = self.client.CreateResource(doc, media=media, collection=folder_resource)
        return doc
    
    def upload_file(self, my_file_path):
        """Upload a file to the specified folder. Then optionally send an email and optionally delete the local file."""
        folder_resource = self._get_folder_resource()
        if not folder_resource:
            raise Exception('Could not find the %s folder' % self.folder)

        doc = self._upload(my_file_path, folder_resource)
                      
        if self.send_email:
            file_link = None
            for link in doc.link:
                if 'drive.google.com' in link.href:
                    file_link = link.href
                    break
            # Send an email with the link if found
            msg = self.message
            if file_link:
                msg += '\n\n' + file_link                
            self._send_email(msg)    

        if self.delete_after_upload:
            os.remove(my_file_path)

if __name__ == '__main__':         
    try:
        if len(sys.argv) < 2:
            exit('Auto Uploader - uploads files to Google Drive\n   by Jeremy Blythe (http://jeremyblythe.blogspot.com)\n\n   Usage: uploader.py {file-path}')
        cfg_path = "/home/"+getpass.getuser()+"/.gdrive.cfg"
        file_path = sys.argv[1]    
        if not os.path.exists(cfg_path):
            exit('Config file does not exist [%s]' % cfg_path)    
        if not os.path.exists(file_path):
            exit('File does not exist [%s]' % file_path)    
        FileUploader(cfg_path).upload_file(file_path)        
    except gdata.client.BadAuthentication:
        exit('Invalid user credentials given.')
    except gdata.client.Error:
        exit('Login Error')
    except Exception as e:
        exit('Error: [%s]' % e)


