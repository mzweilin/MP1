import json
import nltk
import os
import string
import pickle

from collections import Counter

import pylab
import matplotlib.pyplot  as pyplot

from nltk.stem.snowball import EnglishStemmer
stemmer = EnglishStemmer()

tokenizer = nltk.tokenize.treebank.TreebankWordTokenizer()

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

def read_json(file_name_path):
    if not os.path.exists(file_name_path):
        return None
    decoded = json.loads(open(file_name_path).read())
    return decoded

def get_stopwords(file_name = './stopwords.txt'):
    lines = open(file_name).readlines()
    return [line.strip()  for line in lines]


class DocAnalysis:
    punc_list = list(string.punctuation)
    
    def __init__(self, json_folder, ngrams=[1,2], task_name = "DocAnalysis"):
        pass
        self.json_folder = json_folder
        self.counter_folder = "./counter"
        if not os.path.exists(self.counter_folder):
            os.makedirs(self.counter_folder)
            
        self.ngrams = ngrams
        
        self.counter_grams = {}
        for ngram in ngrams:
            self.counter_grams[ngram] = Counter()
        
        self.logger = get_logger(task_name+".log")
        self.task_name = task_name
    
    def analyse(self):
        for root, dirs, files in os.walk(self.json_folder):
        
            pickle_name = root.replace('/', '#') + ".pickle"
            pickle_path = os.path.join(self.counter_folder, pickle_name)
            print pickle_path
            
            counter_folder_grams = {}
            
            if os.path.exists(pickle_path):
                counter_folder_grams = pickle.load(open(pickle_path, "rb"))
                # TODO: merge
                self.merge_counters(counter_folder_grams)
                self.logger.info("Load counter from %s" % pickle_path)
                continue
            for ngram in self.ngrams:
                counter_folder_grams[ngram] = Counter()
                
            for file_name in files:
                # save the counter infor for each folder, then merge
                if file_name[-5:] != ".json":
                    continue
                json_file_path = os.path.join(root, file_name)
                
                try:
                    doc = read_json(json_file_path)
                    self.logger.info("Analyse %s" % json_file_path)
                except:
                    self.logger.error("Can not load %s as json." % json_file_path)
                    continue
                
                # Collect contents from a thread
                contents = []
                thread_title = None
                if doc.has_key('title'):
                    thread_title = doc['title']
                    contents.append(doc['title'])
                
                for post in doc['thread']:
                    if post.has_key('title') and thread_title:
                        if post['title'] != thread_title:
                            contents.append(post['title'])
                    if post.has_key('content'):
                            contents.append(post['content'])
                
                # Count
                for content in contents:
                    tokens = self.str2tokens(content)
                    for ngram in self.ngrams:
                        #self.counter_grams[ngram].update(self.tokens2ngrams(tokens, ngram))
                        counter_folder_grams[ngram].update(self.tokens2ngrams(tokens, ngram))
            
            self.merge_counters(counter_folder_grams)
            if len(counter_folder_grams[1]) > 0:
                pickle.dump(counter_folder_grams, open(pickle_path, "wb"))
                    
            
    def merge_counters(self, counters):
        for ngram in self.ngrams:
            self.counter_grams[ngram] += counters[ngram]
    
    def get_counter(self, ngram):
        if ngram in self.ngrams:
            return self.counter_grams[ngram]
            
    def load_counter(self, file_name = None):
        if file_name == None:
            file_name = self.task_name + ".pickle"
        self.counter_grams = pickle.load(open(file_name, "rb"))
        
    def dump_counters(self, file_name = None):
        if file_name == None:
            file_name = self.task_name# + ".pickle"
        #pickle.dump(self.counter_grams, open(file_name, "wb"))
        for ngram in self.ngrams:
            ngram_file_name = "%s_ngram_%d.pickle" % (file_name, ngram)
            pickle.dump(self.counter_grams[ngram], open(ngram_file_name, "wb"))
    
    
    def get_sorted_counts(self, ngram, tops = None):
        return [tup[1] for tup in self.counter_grams[ngram].most_common(tops)]
    
    def get_sorted_tokens(self, ngram, tops = None):
        return [tup[0] for tup in self.counter_grams[ngram].most_common(tops)]
    
    # Input: string
    # Output: unigram tokens after removing puncuations, stemming, lower_case.
    def str2tokens(self, doc_str):
        tokens = []
        for token in tokenizer.tokenize(doc_str):
            if token in self.punc_list:
                continue
            token_norm = stemmer.stem(token.lower())
            tokens.append(token_norm)
        return tokens
        
    def tokens2ngrams(self, tokens, n):
        if n == 1:
            return tokens
        
        ret = []
        for i in range(0, len(tokens)-n+1):
            ngrams = []
            for j in range(0,n):
                ngrams.append(tokens[i+j])
            ret.append('#'.join(ngrams))
        return ret 
        
    
def main():
    JSON_FOLDER = "./json_samples"
    
    da = DocAnalysis(JSON_FOLDER, ngrams=[1,2], task_name="part2_2nd_run")
    da.analyse()
    #print da.get_counter(1)
    #print da.get_counter(2)
    
    da.dump_counters()
    
    
if __name__ == "__main__":
    main()
