# -*- coding: utf-8 -*-
import numpy as np
import os
import urllib
import gzip
import re
from collections import Counter
import time
import urllib2
from HTMLParser import HTMLParser
import pickle
import sys
import codecs

from pagerank import get_pagerank_simple


DATA_FOLDER = "pagerank_wiki_data"
TIME_RANGE = ["00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23"]
DATE = "20150510"
PAGE_NUM = 10000
START_TIME = time.time()


def get_wikipedia_pageview_top(ymd, page_n):
    print "-- getting wikipedia pageview top --------------"
    data_url = "http://dumps.wikimedia.org/other/pagecounts-raw/"+ymd[0:4]+"/"+ymd[0:4]+"-"+ymd[4:6]+"/pagecounts-"+ymd+"-"
    cnt = Counter()

    def progress(block_count, block_size, total_size):
        percentage = 100.0 * block_count * block_size / total_size
        sys.stdout.write("    getting data ... {0:6.2f} % ( {1:d} KB )\r".format(percentage, total_size/1024))
        sys.stdout.flush()

    for i in TIME_RANGE:
        url = data_url+i+"0000.gz"
        filename = os.path.basename(url)
        print filename
        #get raw data
        if not os.path.exists(DATA_FOLDER):
            os.mkdir(DATA_FOLDER)
        sys.stdout.write("    getting data ... \r")
        sys.stdout.flush()
        if os.path.exists(DATA_FOLDER+"/"+filename):
            print "    getting data ... the file already exists"
        else:
            urllib.urlretrieve(url, DATA_FOLDER+"/"+filename, progress)
            print

        #read data
        print "    reading data ...",
        sys.stdout.flush()
        f = gzip.open(DATA_FOLDER+"/"+filename, "r")
        data = f.read()
        for m in re.findall('^ja\s([^\s]+)\s(\d+)', data, re.M):
            cnt[m[0]] += int(m[1])
        f.close()
        print "done"

    return [c[0] for c in cnt.most_common(page_n)]


def get_wikipedia_page_edge(page_name_list):
    print "-- getting wikipedia page edge -----------------"
    edges = {}

    class WikipediaLinkParser(HTMLParser):
        def __init__(self, pages):
            HTMLParser.__init__(self)
            for page in pages:
                edges[page] = []
                self.page = page
                print "geting html data : "+urllib.unquote(page)+" ...",
                sys.stdout.flush()
                try:
                    connection = urllib.urlopen("http://ja.wikipedia.org/wiki/"+page)
                    encoding = connection.headers.getparam('charset')
                    self.in_main = False
                    self.div_count = 1
                    self.feed(connection.read().decode(encoding))
                    connection.close()
                    print "done"
                except urllib2.HTTPError:
                    print "fail : HTTPError"

        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if self.in_main:
                if tag == "div":
                    self.div_count += 1
                else:
                    if tag == "a" and "href" in attrs and attrs["href"].startswith("/wiki/"):
                        link_to = str(attrs["href"][6:])
                        if not link_to in edges[self.page]:
                            edges[self.page].append(link_to)
            else:
                if tag == "div" and "role" in attrs and attrs["role"] == "main":
                    self.in_main = True

        def handle_endtag(self, tag):
            if self.in_main and tag == "div":
                self.div_count -= 1
                if self.div_count == 0:
                    self.in_main = False

    WikipediaLinkParser(page_name_list)
    return edges


def make_transition_probability_matrix(page_name_list, edges, page_n):
    print "-- making transition probability matrix --------"
    print "calculating ...",
    sys.stdout.flush()
    M = np.zeros([page_n, page_n])
    for i in xrange(page_n):
        page = page_name_list[i]
        dest_indexs = []
        for dest in edges[page]:
            if page == dest:
                continue
            try:
                j = page_name_list.index(dest)
                dest_indexs.append(j)
            except ValueError:
                pass
        dest_num = len(dest_indexs)
        if dest_num:
            p_ji = 1./dest_num
            for j in dest_indexs:
                M[j][i] = p_ji
        else:
            M[i][i] = 1.
    print "done"
    return M


def get_wikipedia_pagerank(M, alpha, err_dest, return_P):
    print "-- calculate pagerank --------------------------"
    print "calculating ...",
    sys.stdout.flush()
    rank, P = get_pagerank_simple(M, alpha, err_dest, return_P)
    print "done"
    return rank, P


def get_from_file_or_func(name, func, *arg):
    filepath = DATA_FOLDER+"/"+name
    if not os.path.exists(filepath):
        obj = func(*arg)
        if not os.path.exists(DATA_FOLDER):
            os.mkdir(DATA_FOLDER)
        f = open(filepath, "w")
        pickle.dump(obj, f)
        f.close()
    else:
        f = open(filepath, "r")
        obj = pickle.load(f)
        f.close()
    print "elapsed time : {0:.0f}m {1:.1f}s".format(*divmod(time.time()-START_TIME, 60))
    return obj


def wikipedia_pagerank(ymd, page_n, save=False, alpha=0.85, err_dest=0.0001):
    page_name_list = get_from_file_or_func("page_name_list(n={0}).dump".format(page_n), get_wikipedia_pageview_top, ymd, page_n)

    edges = get_from_file_or_func("edge(n={0}).dump".format(page_n), get_wikipedia_page_edge, page_name_list)
    M = get_from_file_or_func("M(n={0}).dump".format(page_n), make_transition_probability_matrix, page_name_list, edges, page_n)
    rank, P = get_from_file_or_func("rank(n={0}).dump".format(page_n), get_wikipedia_pagerank, M, alpha, err_dest, True)

    print "-- result --------------------------------------"
    if save:
        print "write to "+DATA_FOLDER+"/result.txt"
        out = codecs.open(DATA_FOLDER+"/result.txt", "w", "utf-8")
    else:
        out = sys.stdout
    for i in xrange(page_n):
        try:
            out.write(unicode("{0:5d} : {1:.5f} : {2}\n".format(i+1, P[rank[i]], urllib.unquote(page_name_list[rank[i]])), encoding="utf-8"))
        except:
            out.write("{0:5d} : {1:.5f} : {2}\n".format(i+1, P[rank[i]], page_name_list[rank[i]]))
    if save:
        out.close()
    print "elapsed time : {0:.0f}m {1:.1f}s".format(*divmod(time.time()-START_TIME, 60))


if __name__ == "__main__":
    wikipedia_pagerank(DATE, PAGE_NUM, save=True)
