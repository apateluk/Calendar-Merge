import os
import ics
import logging
import sys
import threading
from time import sleep
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

cal_filename = "/data/calendars.txt"
api_key = ""

cal_lock=threading.Lock()

class MyServer(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_paramaters = parse_qs(parsed_url.query)

        if "key" not in query_paramaters:
            print("Key does not exist")
            self.send_response(401)
            self.end_headers()
            return

        if query_paramaters["key"][0] != api_key:
            print("Invalid Key")
            self.send_response(401)
            self.end_headers()
            return

        self.send_response(200)
        self.end_headers()
        cal_lock.acquire()
        with open("my.ics", "rb") as cal:
            self.wfile.write(cal.read())
            cal.close()
        cal_lock.release()

def calender_merge_thread(name):
    while(True):
        print("Updating Calendars\n")
        
        file_opened_successfully = False
        try:
            cal_file = open(cal_filename, "r")
            file_opened_successfully = True
        except FileNotFoundError:
            print("file {} does not exist".format(cal_filename))

        if file_opened_successfully == True:
            urls = cal_file.readlines()
            cal_file.close()

            cal = ics.Calendar()

            for url in urls:
                clean_url = url.strip()
                print(clean_url)
                cal.events.extend(ics.Calendar(requests.get(clean_url).text).events)

            cal.events.sort()
            print(cal)
            p = os.path.abspath('my.ics')
            cal_lock.acquire()
            with open(p, 'w') as f:
                f.writelines(cal)
            f.close()
            cal.events.clear()
            cal_lock.release()

        sleep(60*30) #Sleep for 30mins


if __name__ == "__main__":
    import requests

    if len(sys.argv) > 1:
        cal_filename = sys.argv[1]
    
    if os.path.exists(cal_filename) is not True:
        print("File {} does not exist".format(cal_filename))
        cal_filename = "example_calendar.txt"
    
    api_key = os.environ.get('CALMERGE_API_KEY')
    if (api_key is None):
        print("API key is not set, exiting")
        sys.exit(1)
    
    cal_thread = threading.Thread(target=calender_merge_thread, args=(1,), daemon=True)
    cal_thread.start()
    print("Starting Calendar Web Server\n")
    myServer = HTTPServer(('', 8080), MyServer)
    myServer.serve_forever()
    myServer.server_close()



