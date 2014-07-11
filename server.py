import json
import sys
import httplib
import BaseHTTPServer
import socket
import urlparse
import web_server
import shutil
import os
import sqlite3
import errno
import traceback

def run(handler_class, port):
    server_address = ('', port)
    httpd = BaseHTTPServer.HTTPServer (server_address, handler_class)
    httpd.serve_forever()
conn = sqlite3.connect(r"spending.db")
conn.commit()
conn.close()

class Handler(BaseHTTPServer.BaseHTTPRequestHandler, web_server.BaseHandler):
  server_version = "library/0.1"
  def loadFile(self, fileName):
    try:
      f=open(fileName)
    except:
      try:      
        fileName="/usr/service/pub/"+fileName   
        f=open(fileName)
      except IOError as err:
        if err.errno != errno.ENOENT:
          traceback.print_exc()
          self.web_error(httplib.INTERNAL_SERVER_ERROR, "Unexpected exception")
        else:
          self.web_error(httplib.NOT_FOUND)
        
    contents=f.readlines()
    f.close()
    self.loadFile2(contents, fileName)
 
  def loadFile2 (self, contents, pathelem):
    self.send_response(httplib.OK)
    if "css" in pathelem:
      self.send_header("content-type", "text/css")
    else:
      self.send_header("content-type", "text/html")
    self.send_header("content-length", os.path.getsize(pathelem))
    self.end_headers()
    self.wfile.writelines(contents)


  def do_GET(self):
    path_elements=self.path.split('/')[1:]

    if path_elements[0] =='':
    # entry point
        self.send_response(httplib.FOUND)
        self.send_header("Location", "datachart.html")
        self.end_headers()
    
    elif path_elements[0]=='datachart.html':
        data = open('data.txt', 'w')        
        try:
          db = sqlite3.connect('borrowedBooks.db')
          cursor = db.cursor()
          cursor.execute('''
              SELECT * FROM Books ORDER BY date''')        

          for row in cursor.fetchall():
            data.write(str(row[0])+', '+str(row[1])+', '+str(row[2])+'\n')
          db.close()
        except:
          data.write("")
        
        data.close()
        self.loadFile(path_elements[0])  
    else:    
        self.loadFile(path_elements[0])    


  def do_POST(self):
    path_elements=self.path.split('/')[1:]

    if path_elements[0] == 'datachart.html':
      form_values = self.read_x_www_form_urlencoded_request_body()
      book = self.single_value(form_values, 'bookName', "form")
      date = self.single_value(form_values, 'date', "form")
      if book is None or date is None:
        self.web_error(httplib.BAD_REQUEST, 
          "Bad form, must provide all information")
      else: 
        db = sqlite3.connect('borrowedBooks.db')
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE if not exists Books 
                (id INTEGER primary key autoincrement, 
                 book TEXT, date DATE)''')
        cursor.execute ('''
            INSERT INTO Books(book, date)
            VALUES(?,?)''',(book, date))
        db.commit()
        db.close()

        self.send_response(httplib.FOUND)
        self.send_header("Location", "/datachart.html")
        self.end_headers()

  def do_DELETE(self):
    path_elements=self.path.split('/')[1:]

    if path_elements[0] == 'datachart.html':
      raw_body = self.read_request_body()
      form_values=urlparse.parse_qs(raw_body)
      delID=form_values['id']

      db = sqlite3.connect('borrowedBooks.db')
      cursor=db.cursor()
      cursor.execute('''DELETE FROM Books WHERE id='''+ delID[0])
      db.commit()
      db.close()

      self.send_response(httplib.SEE_OTHER)
      self.send_header("Location", "/datachart.html")
      self.end_headers() 

  def do_UPDATE(self):
    path_elements=self.path.split('/')[1:]

    if path_elements[0] == 'datachart.html':
      raw_body = self.read_request_body()
      form_values = urlparse.parse_qs(raw_body)
      idb = form_values['idb']
      newDate = form_values['newDate']

      db = sqlite3.connect('borrowedBooks.db')
      cursor=db.cursor()
      cursor.execute("UPDATE Books SET date=? WHERE id=?", (newDate[0],idb[0]))
      db.commit()
      db.close()

      self.send_response(httplib.OK)
      self.send_header("Location", "/datachart.html")
      self.end_headers() 
 
if __name__ == '__main__':
    port = int(sys.argv[1])
    run(Handler, port)   

