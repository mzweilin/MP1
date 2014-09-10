import bs4
from bs4 import BeautifulSoup
import time, json

class Post:   
    def __init__(self, pid):
        self.info = {}
        self.info['postID'] = pid
    
    def setAuthor(self, author):
        self.info['author'] = author
    
    def setAuthorID(self, author_id):
        self.info['authorID'] = author_id
    
    def setDate(self, timestamp):
        self.info['date'] = time.strftime("%Y%m%d-%H:%M:%S -0400", timestamp)
    
    def setContent(self, content):
        self.info['content'] = content 
   
    def setReplyToID(self, rid):
        self.info['replyToID'] = rid
   
    def get_dict(self):
        return self.info

class Thread:
    def __init__(self, title, url):
        self.info = {}
        self.info['title'] = title
        self.info['URL'] = url
        self.info['thread'] = []
      
    def add_posts(self, posts):
        for post in posts:
            print post.get_dict()
            self.info['thread'].append(post.get_dict())

    def to_json(self):
        return json.dumps(self.info)
    
class Wrapper:
    def __init__(self):
        pass
        
    def parse_file(self, file_path):
        self.soup = BeautifulSoup(open(file_path))
        self.postElms = []
        self.thread = self.extract_all()
        print "Parse %s" % file_path
    
    def parse_extend_file(self, file_path):
        self.soup = BeautifulSoup(open(file_path))
        self.postElms = self.soup.find_all("div", attrs={'class': 'post_data'})
        
        m_posts = []
        for elm in self.postElms:
            if "post_" in elm.get('id'):
                m_posts.append(self.extract_post(elm))
        self.thread.add_posts(m_posts)
        print "Extend parse %s" % file_path
        
    
    def to_json(self):
        return self.thread.to_json()
    
    def extract_all(self):
        thread = self.extract_thread_info()
        m_posts = []
        
        first_post = self.extract_first_post(self.postElms.pop(0))
        m_posts.append(first_post)
        
        
        for elm in self.postElms:
            if "post_" in elm.get('id'):
                m_posts.append(self.extract_post(elm))
        thread.add_posts(m_posts)
        
        return thread
        
    def extract_thread_info(self):
        m_threadURL = self.soup.find("link", attrs={'rel':'canonical'}).get('href')
        
        m_threadTitle = ""
        h1 = self.soup.find("h1")
        if h1:
            m_threadTitle = h1.contents[0]
        else:
            m_threadTitle = self.soup.find('div', attrs={'class': 'desc'}).get('title')
            
        self.postElms.extend(self.soup.find_all("div", attrs={'class': 'post_data'}))
        return Thread(m_threadTitle, m_threadURL)

    def extract_first_post(self, elm):
        p = Post(elm.get("id"))
        
        author_info = self.soup.find("div", attrs={'class': 'post_info'}).find(attrs={'class': 'user_info'})
        author_name = author_info.find('a')

        p.setAuthor(author_name.contents[0])
        p.setAuthorID(author_name.get("href"))

        #author_info.contents
        for span in author_info.find_all('span'):
            #print span.get('class')
            if span.get('class') and 'separator' in span.get('class'):
                date_text = str(span.next.next).strip()

        p.setDate(self.ts_from_text(date_text))

        #post content
        contents = unicode("")
        for frag in elm.find('div', attrs={'class':'KonaBody'}).contents:
            if frag.string:
                contents = contents + unicode(frag.string).strip()
        p.setContent(contents) #strip()

        return p
    
    def extract_post(self, elm):
        p = Post(elm.get('id'))
        user_info = elm.find(attrs={'class': 'user_info'})
        
        #post_question_forum_to
        replyToID = user_info.find(attrs={'class': 'post_question_forum_to'})
        if replyToID:
            if replyToID.find('a'):
                p.setReplyToID(replyToID.find('a').get('href'))
            else:
                p.setReplyToID(self.extractReplyToID(replyToID.contents[0]))
        
        #timestamp
        author_info = elm.find('div', attrs={'class': 'question_by'})
        author_name = author_info.find('a')

        #author_info.contents[0]
        #author_info.get("href")
        p.setAuthor(author_name.contents[0])
        p.setAuthorID(author_name.get("href"))
        
        date_text = ""
        for span in author_info.find_all('span'):
            #print span.get('class')
            if span.get('class') and 'separator' in span.get('class'):
                date_text = str(span.next.next).strip()
        
        p.setDate(self.ts_from_text(date_text))
        
        #post content
        contents = unicode("")
        for frag in elm.find('div', attrs={'class':'KonaBody'}).contents:
            if frag.string:
                #print frag.string.strip()
                contents = contents + unicode(frag.string).strip()
        p.setContent(contents) #strip()
        
        return p
        
    def extractReplyToID(self, text):
        return text[4:].strip()

    def ts_from_text(self, text):
        try:
            timestamp = time.strptime(date_text, "%b %d, %Y")
            return timestamp
        except:
            return time.localtime()
        
if __name__ == "__main__":
    wrapper = Wrapper()
    for page_num in range(1,6):
        html_file = "./html_samples/wx4ed-thread-269787-p%d.html" % page_num
        if page_num == 1:
            wrapper.parse_file(html_file)
        else:
            wrapper.parse_extend_file(html_file)
        
    print wrapper.to_json()
    
