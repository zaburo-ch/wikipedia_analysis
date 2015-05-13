import urllib
import os
import gzip
import re
from collections import Counter
import sys
import time
import urllib2


RAW_DATA_FOLDER = "rawdata"
START_TIME = time.time()
TIME_RANGE = ["00","01","02","03","04","05","06","07","08","09","10","11","12","13","14","15","16","17","18","19","20","21","22","23"]
LIST_SIZE = 10000

cnt = Counter()
matrix = {}
mostCommon = []
roots = []
INF = 100000000

def progress( block_count, block_size, total_size ):
  percentage = 100.0 * block_count * block_size / total_size
  sys.stdout.write( "%.2f %% ( %d KB )\r"%(percentage,total_size/1024))

def getPagecountData(url):
  if not os.path.exists(RAW_DATA_FOLDER):
    os.mkdir(RAW_DATA_FOLDER)
  filename = os.path.basename(url)
  print "get data:"+filename
  if os.path.exists(RAW_DATA_FOLDER+"/"+filename):
    print "the file already exists"
  else:
    urllib.urlretrieve(url,RAW_DATA_FOLDER+"/"+filename,progress)

def readData(url):
  filename = os.path.basename(url)
  print "read data from "+filename
  f = gzip.open(RAW_DATA_FOLDER+"/"+filename,"r")
  data = f.read()
  for m in re.findall('^ja\s([^\s]+)\s(\d+)',data,re.M):
    #print m[0]+":"+m[1]
    cnt[m[0]] += int(m[1])
  f.close()

def printResult():
  counter = 1
  for page in mostCommon:
    sys.stdout.write("%4d:%s %d\n"%(counter,urllib.unquote(page[0]),page[1]))
    counter+=1

def writeResult(filename):
  counter = 1
  f = open(filename,'w')
  for page in mostCommon:
    f.write("%4d:%s %d\n"%(counter,urllib.unquote(page[0]),page[1]))
    counter+=1
  f.close()

def prepareMatrix():
  print "prepare matrix"
  for page1 in mostCommon:
    matrix[page1[0]] = {}
    for page2 in mostCommon:
      if page1==page2:
        matrix[page1[0]][page2[0]] = 0
      else:
        matrix[page1[0]][page2[0]] = INF

def setData():
  print "set data"
  for key in matrix.keys():
    print "get html data : "+urllib.unquote(key)
    try:htmldata = urllib2.urlopen("http://ja.wikipedia.org/wiki/"+key)
    except urllib2.HTTPError, e:
      print "fail!"
    for m in re.findall('<a href="/wiki/([^"]+)"',htmldata.read()):
      if m in matrix.keys() and matrix[key][m]==INF:
        #print "find root "+urllib.unquote(key)+" to "+urllib.unquote(m)
        matrix[key][m] = 1

def warshallFloyd():
  print "Doing Warshall-Floyd Algorithm"
  for k in matrix.keys():
    for i in matrix.keys():
      for j in matrix.keys():
        matrix[i][j] = min(matrix[i][j],matrix[i][k]+matrix[k][j])

class Root:
  def __init__(self, start, goal, dist):
    self.start = start
    self.goal = goal
    self.dist = dist

def cmp(x, y):
  a = x.dist
  b = y.dist
  if a == b: return 0
  if a < b: return 1
  return -1

def pickUpRoot():
  print "pick up valid roots"
  for i in matrix.keys():
    for j in matrix.keys():
      if matrix[i][j] < INF:
        roots.append(Root(i,j,matrix[i][j]))

def longestRoot():
  roots.sort(cmp)
  counter = 1
  for r in roots:
    sys.stdout.write("%4d:%3d %s -> %s\n"%(counter,r.dist,urllib.unquote(r.start),urllib.unquote(r.goal)))
    counter+=1

if __name__ == "__main__":
  if len(sys.argv)==2:
    ymd = str(sys.argv[1])
    if len(ymd)==8:
      dataUrl = "http://dumps.wikimedia.org/other/pagecounts-raw/"+ymd[0:4]+"/"+ymd[0:4]+"-"+ymd[4:6]+"/pagecounts-"+ymd+"-"
      for i in TIME_RANGE:
        tempurl = dataUrl+i+"0000.gz"
        getPagecountData(tempurl)
        print "elapsed_time:"+str((time.time()-START_TIME)/60)+"minutes"
        readData(tempurl)
        print "elapsed_time:"+str((time.time()-START_TIME)/60)+"minutes"
      mostCommon = cnt.most_common(LIST_SIZE)
      #printResult()
      #writeResult(ymd+".txt")
      prepareMatrix()
      setData()
      print "elapsed_time:"+str(time.time()-START_TIME)+"seconds"
      warshallFloyd()
      print "elapsed_time:"+str(time.time()-START_TIME)+"seconds"
      pickUpRoot()

      print "---------------------------------------------------------"
      print
      print "List of longest distance between Wikipedia pages"
      print ymd+" : Page view Top "+str(LIST_SIZE)
      print
      longestRoot()
      print
      print "elapsed_time:"+str((time.time()-START_TIME)/60)+"minutes"
