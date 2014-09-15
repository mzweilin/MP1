from bs4 import BeautifulSoup
import json, os, time, urllib2, StringIO, gzip
import Wrapper_MedHelp

def get_logger(file_name = None):
    import logging
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # create a file handler
    
    if file_name:
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
    
    
    TOPICS = ['Depression', 'Depression-Support-For-Families-', "Eye-Care"]
    starting_urls = {'Depression': 'http://www.medhelp.org/forums/Depression/show/57',
                     'Depression-Support-For-Families-': 'http://www.medhelp.org/forums/Depression-Support-For-Families-/show/1259',
                     'Eye-Care': 'http://www.medhelp.org/forums/Eye-Care/show/43',
                     }
    
    if WORK_DIR:
        os.chdir(WORK_DIR)
    
    logger = get_logger("wrapper.log")
    
    wrapper = Wrapper_MedHelp.Wrapper(logger)
    
    #for topic in ['']:
    for (topic, starting_url) in starting_urls.items():
        html_folder = os.path.join(HTML_FOLDER, topic)
        json_folder = os.path.join(JSON_FOLDER, topic)
        if not os.path.exists(json_folder):
            os.makedirs(json_folder)
        
        for html_file in os.listdir(html_folder):
            fname, ext = os.path.splitext(html_file)
            if ext != ".html" or fname[-2:] != "p1":
                continue
            
            html_file_path = os.path.join(html_folder, html_file)
            json_file_name = fname[:-3] + ".json"
            json_file_path = os.path.join(json_folder, json_file_name)
            if os.path.exists(json_file_path) and os.path.getsize(json_file_path)>0:
                logger.info('skip file: %s' % json_file_path)
                continue
            
            # parse the first page
            try:
                wrapper.parse_file(html_file_path)
            except:
                logger.warning("Could not parse: %s", html_file_path)
                continue
            
            page_num = 2
            file_name = "%s%d.html" %(fname[:-1], page_num)
            file_path = os.path.join(html_folder, file_name)
            
            # potentially parse the following pages
            while os.path.exists(file_path):
                print "exist"
                wrapper.parse_extend_file(file_path)
                page_num += 1
                file_name = "%s%d.html" %(fname[:-1], page_num)
                file_path = os.path.join(html_folder, file_name)
            
            json_str = wrapper.to_json()
            
            
            
            json_writer = open(json_file_path, 'w')
            json_writer.write(wrapper.to_json())
            json_writer.close()
        
if __name__ == "__main__":
    #test()
    main()
