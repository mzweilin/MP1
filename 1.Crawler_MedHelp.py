# 1. starting page of each topic: URL
# 2. fetch the URL list of each thread, download the thread page, parse, if more pages in thread, get more, parse
# 3. traverse the pages by changing URL, ?page=1

# read the first page
# parse, and get the thread list
# if the thread list is empty, terminate.
# else 
#     for loop
#       featch one thread page
#       parse, get the info
#       if more page? then fetch that page, parse, get the info
#  

#import Wrapper.thread_url_extractor
from bs4 import BeautifulSoup
import json, os, time, urllib2, StringIO, gzip

class Clawler:
    def __init__(self, html_dir, header, logger):
        self.html_dir = html_dir
        #self.json_dir = json_dir
        self.http_req_header = header
        self.page = 0
        self.logger = logger
    
    # DONE
    def get_next_page_url(self):
        self.page += 1
        return "%s?page=%d" % (self.starting_url, self.page)
    
    # DONE
    # simple wrapping on 
    #
    def get_next_comment_page_url(self, html_str):
        soup = BeautifulSoup(html_str)
        next_page_msg= soup.find('a', attrs={'class': "msg_next_page"})
        if next_page_msg:
            return next_page_msg.get('href')
    
    
    def get_previous_comment_page_url(self, html_str):
        soup = BeautifulSoup(html_str)
        previous_page_msg= soup.find('a', attrs={'class': "msg_previous_page"})
        if previous_page_msg:
            return previous_page_msg.get('href')
    
    
    # DONE.
    def curl_str(self, url):
        #time.sleep(1)
        if url[:4] != "http":
            url = "http://www.medhelp.org/" + url
        request = urllib2.Request(url, headers=self.http_req_header)
        try:
            opener = urllib2.urlopen(request)
            contents = opener.read()
        except:
            self.logger.warning("Failed when accessing %s"  % (url))
            return None
        self.logger.info("Fetch %d bytes from %s"  % (len(contents), url))
        
        data = StringIO.StringIO(contents)
        gzipper = gzip.GzipFile(fileobj=data)
        html_str = gzipper.read()
        return html_str
    
    
    # DONE. 
    # save the thread page to html file, return the next comment page if it has one.
    def fetch_thread_page(self, thread_url, page_num):
        thread_id = (thread_url.split('/')[-1]).split('?')[0]# + "-" + thread_url.split('/')[-3]
        file_name = "wx4ed-thread-%s-p%d.html" % (thread_id, page_num)
        file_path = os.path.join(self.html_dir,file_name)
        
        if thread_url.find('?page=') < 0:
            thread_url = thread_url + "?page=%d" % page_num
        
        html_str = ""
        
        if os.path.exists(file_path) and os.path.getsize(file_path)>0:
            #read from file system
            html_str = open(file_path).read()
            self.logger.info('read %s from file' % (thread_id))
        else:
            html_str = self.curl_str(thread_url)
            while not html_str:
                time.sleep(1)
                html_str = self.curl_str(thread_url)
        
            local_file = open(file_path, "w")
            local_file.write(html_str)
            local_file.close()
        
        return self.get_next_comment_page_url(html_str)
    
    # DONE
    # simple wrapping on the thread list page
    def extract_thread_url_list(self, url):
        html_str = self.curl_str(url)
        
        soup = BeautifulSoup(html_str)
        urls = []
        for thread_summary in soup.find_all('div', attrs={'class': 'subject_summary'}):
            url = thread_summary.find('a').get('href')
            urls.append(url)
        
        return urls
        
    def run(self, starting_url):
        self.starting_url = starting_url
        self.page = 0
        while True:
            url = self.get_next_page_url()
            thread_url_list = self.extract_thread_url_list(url)
            if len(thread_url_list) == 0:
                break
            
            for thread_url in thread_url_list:
                page_num = 1
                next_page_url = self.fetch_thread_page(thread_url, page_num)
                while next_page_url:
                    page_num += 1
                    next_page_url = self.fetch_thread_page(next_page_url, page_num)
    
    def test_multi_page_thread(self, thread_url):
        page_num = 1
        next_page_url = self.fetch_thread_page(thread_url, page_num)
        while next_page_url:
            page_num += 1
            next_page_url = self.fetch_thread_page(next_page_url, page_num)

def get_http_header():
    headers_har = [
                {
                  "name": "Accept-Encoding",
                  "value": "gzip,deflate"
                },
                {
                  "name": "Host",
                  "value": "www.medhelp.org"
                },
                {
                  "name": "Accept-Language",
                  "value": "en-US,en;q=0.8,zh-CN;q=0.6,zh-TW;q=0.4"
                },
                {
                  "name": "User-Agent",
                  "value": "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.143 Safari/537.36"
                },
                {
                  "name": "Accept",
                  "value": "text/javascript, text/html, application/xml, text/xml, */*"
                },
                {
                  "name": "Connection",
                  "value": "keep-alive"
                }
              ]

    headers_custom = dict()

    for item in headers_har:
        key = item['name']
        value = item['value']
        headers_custom[key] = value
    
    return headers_custom
    
def test():
    headers_custom = get_http_header()
    html_dir = "./test-download"
    #json_dir = 
    starting_url = "http://www.medhelp.org/forums/Depression/show/57"
    
    if not os.path.exists(html_dir):
        os.makedirs(html_dir)
        
    c = Clawler(html_dir, headers_custom, get_logger("crawler.log"))
    #c.run(starting_url)
    c.test_multi_page_thread("http://www.medhelp.org/posts/Depression/How-long-is-Effexor-withdrawal-supposed-to-last/show/269787?page=1")
 
def get_logger(file_name):
    import logging

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # create a file handler
    handler = logging.FileHandler(file_name)
    handler.setLevel(logging.INFO)

    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(handler)
    
    return logger

def main():
    WORK_DIR = "./"
    HTML_FOLDER = "data/html/MedHelp/"
    JSON_FOLDER = "data/json/MedHelp/"
    
    starting_urls = {'Depression': 'http://www.medhelp.org/forums/Depression/show/57', # 610 pages * 20 = 12200 threads
                     'Depression-Support-For-Families-': 'http://www.medhelp.org/forums/Depression-Support-For-Families-/show/1259', # 5 pages * 20 = 100 threads
                     'Eye-Care': 'http://www.medhelp.org/forums/Eye-Care/show/43', #1360 pages * 20 = 27200 threads
                     }
    os.chdir(WORK_DIR)
    
    headers_custom = get_http_header()
    logger = get_logger("crawler.log")
    
    for (topic, starting_url) in starting_urls.items():
        html_folder = os.path.join(HTML_FOLDER, topic)
        #json_folder = os.path.join(JSON_FOLDER, topic)
        if not os.path.exists(html_folder):
            os.makedirs(html_folder)
        
        c = Clawler(html_folder, headers_custom, logger)
        c.run(starting_url)
        
if __name__ == "__main__":
    #test()
    main()

