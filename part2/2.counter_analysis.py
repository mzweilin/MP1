import pickle
import pylab
import matplotlib.pyplot  as pyplot
from collections import Counter

def get_stopwords(file_name = './stopwords.txt'):
    lines = open(file_name).readlines()
    return [line.strip()  for line in lines]

class CounterAnalysis:
    def __init__(self, file_name):
        self.counter = pickle.load(open(file_name, "rb"))
        pass
    
    def get_sorted_counts(self, tops = None):
        return [tup[1] for tup in self.counter.most_common(tops)]
    
    def get_sorted_tokens(self, tops = None):
        return [tup[0] for tup in self.counter.most_common(tops)]
    
    def draw_loglog_plot_old(self, a, file_name=None):
        #a = [ pow(10,i) for i in range(10) ]
        pyplot.axis('equal')
        fig = pyplot.figure()
        ax = fig.add_subplot(2,1,1)
        
        line, = ax.plot(a, color='blue', lw=2)
        
        ax.set_xscale('log')
        ax.set_yscale('log')
        
        if file_name:
            pylab.savefig(file_name)
        else:
            pylab.show()
    
    def draw_loglog_plot(self, a, file_name=None):
        x = [i for i in xrange(1, len(a)+1)]
        y = a
        pyplot.loglog(x,y,'ro',basex=2,basey=2)
        pyplot.xlim([1,2**29])
        pyplot.ylim([1,2**29])
        #pyplot.axis('scaled')
        pyplot.show()
    
    def compare_stopwords(self):
        smart_stopwords = get_stopwords()
        k = len(smart_stopwords)
        my_stopwords = self.get_sorted_tokens(k)
        
        smart_stopwords_counter = Counter()
        
        for stopword in smart_stopwords:
            if self.counter.has_key(stopword):
                smart_stopwords_counter[stopword] = self.counter[stopword]
            else:
                smart_stopwords_counter[stopword] = 0
        
        print my_stopwords
        print smart_stopwords_counter
        
        
        
        
        
        
        common_words = []
        rare_words = []
        popular_words = []
        
        for stopword in smart_stopwords:
            if stopword in my_stopwords:
                #print stopword
                common_words.append(stopword)
            else:
                rare_words.append(stopword)
        for stopword in my_stopwords:
            if stopword not in smart_stopwords:
                popular_words.append(stopword)
         
        
        print "K=%d" % len(smart_stopwords)
        print "KM=%d" % len(my_stopwords)
        print "Keep the %d common stopwords" % len(common_words)
        print "Remove the %d rare words" % len(rare_words)
        print "Add the %d popular words" % len(popular_words)
        
        
        
        
        
def main():
    file_list = {'unigram': "part2_2nd_run_ngram_1.pickle", 'bigram': "part2_2nd_run_ngram_2.pickle"}
    
    file_name = file_list['bigram']
    
    ca = CounterAnalysis(file_name)
    
    # vocabulary size
    #print "Vocabulary size: %d" % len(ca.get_sorted_tokens())
    
    ca.draw_loglog_plot(ca.get_sorted_counts(), "unigram-zips-law.png")
    #ca.compare_stopwords()

if __name__ == "__main__":
    main()
