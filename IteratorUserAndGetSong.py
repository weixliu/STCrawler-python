import urllib2
import urllib
import time
import re
import os
import sys

def callbackfunc(blocknum, blocksize, totalsize):
    percent = 100.0 * blocknum * blocksize / totalsize
    if percent > 100:
        percent = 100
    print "%.2f%%" % percent

SongTypeDict = {
    "7d99bb4c7bd4602c342e2bb826ee8777":".wma",
    "25e4f07f5123910814d9b8f3958385ba":".Wma",
    "51bbd020689d1ce1c845a484995c0cce":".WMA",
    "b3a7a4e64bcd8aabe4cabe0e55b57af5":".mp3",
    "d82029f73bcaf052be8930f6f4247184":".MP3",
    "5fd91d90d9618feca4740ac1f2e7948f":".Mp3"
}

def getListIndex(l, index, default):
    if len(l) > index:
        return l[index]
    else:
        return default

def extractRealSongURL(playIcon,strID,strURL,intWidth,intHeight,stype,sHead,st_songid,t):
    if strURL.find('rayfile') > 0:
        realURL = sHead + strURL + SongTypeDict[stype]
    else:
        url = 'http://songtaste.com/time.php'
        values = {
            "str":strURL,
            "sid":st_songid,
            "t":t
        }
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        realURL = response.read()
    return realURL


def extractSongURL( url ):
    responseL = urllib2.urlopen(url)
    if responseL.geturl() != url:
        print url
        return "error about this song"
    HTMLSource = responseL.read()
    patternStr = r'<a href="javascript:playmedia1\(\'(.*?)\',\'(.*?)\', \'(.*?)\', \'(.*?)\', \'(.*?)\', \'(.*?)\', \'(.*?)\', \'(.*?)\',(.*?)\);ListenLog'
    pattern = re.compile( patternStr, re.S)
    params = re.findall( pattern, HTMLSource )
    if len(params) == 0:
        realSongURL = 'http://m0.songtaste.com/201508011045/c0ce301a74b500d259c4d2bd1925f012/0/02/028e905907fbcba27d7543a5902de978.mp3'
        realSongPattern = r'http://.*?.(mp3|MP3|Mp3|wma|WMA|Wma)'
        rsp = re.compile( realSongPattern,re.S )
        results = re.findall( rsp, HTMLSource )
        print results[0]
    elif len(params) == 1:
        playIcon = params[0][0]
        strID = params[0][1]
        strURL = params[0][2]
        intWidth = params[0][3]
        intHeight = params[0][4]
        stype = params[0][5]
        sHead = params[0][6]
        st_songid = params[0][7]
        t = params[0][8] 
        return extractRealSongURL(playIcon,strID,strURL,intWidth,intHeight,stype,sHead,st_songid,t)
    else:
        print "some error happen with extractSongInfo in HTMLSource"
        print params

inputUserID = int(sys.argv[1])
#main process , change range number is UserID,[start,end)
for uid in range(inputUserID,inputUserID + 1):
    path = "./%d" % uid
    if not os.path.exists(path):
        os.mkdir(path)
    for tries in range(10):
        try:
            userURL = 'http://www.songtaste.com/user/%d/' % uid
            response = urllib2.urlopen( userURL )
            #sleep for 10ms
            if response.geturl() == userURL:
                print "%s is valid" % userURL
                #extend the url to http://www.songtaste.com/user/%d/allrec/
                songNumStr1 = r'<p class="more"><a href="/user/.*?/allrec" class="underline">(.*?)</a></p>'
                songNumStr2 = r'\d\d*'
                HTMLSource = response.read()
                SongNumStrList = re.findall( re.compile(songNumStr1, re.S), HTMLSource )
                if len(SongNumStrList) != 0:
                    NumList = re.findall( re.compile(songNumStr2, re.S), SongNumStrList[0] )
                    if len(NumList) != 0:
                        songNum = int( NumList[0] )
                        print "the %d user rec %d songs" % (uid, songNum)
                    userRecSongListURL = userURL + 'allrec/'
                    print "get user allrec song url:%s" % userRecSongListURL
                    pageStr = r"<a href='/user/.*?/allrec/(\d*)'>"
                    innerRes = urllib2.urlopen( userRecSongListURL )
                    innerSrc = innerRes.read()
                    pageList = re.findall( re.compile(pageStr, re.S), innerSrc )
                    PageNum = 1 if len(pageList) == 0 else int( pageList[len(pageList) - 1] )
                    print "the user has %d pages" % PageNum
                    for page in range(PageNum):
                        #url = userRecSongListURL + '/%d' % (page + 1)
                        realURL = userRecSongListURL + '/%d' % (page + 1)
                        print "get page %d" % (page + 1)
                        response3 = urllib2.urlopen( realURL )
                        source3 = response3.read()
                        pattern = re.compile(r'WL\("(.*?)", "(.*?)","(.*?)","(.*?)"\);',re.S)
                        result3 = re.findall( pattern, source3 )
                        for ritem in result3:
                            Idx = ritem[0]
                            SongID = ritem[1]
                            SongName = ritem[2]
                            UpDT = ritem[3]
                            songURL = 'http://www.songtaste.com/song/%s/' % SongID
                            songRealURL = extractSongURL( songURL )
                            print songRealURL
                            if songRealURL != "error about this song":
                                tail = songRealURL[ songRealURL.rfind('.'): ]
                                local = '.\%d\%s%s' % (uid, re.sub(r'(<|>|:|"|/|\\|\||\?|\*)', ' ', SongName), tail)
                                urllib.urlretrieve( songRealURL, local, callbackfunc )
                else:
                    print 'null'

            else:
                print "%s is invalid" % userURL
            break
        except urllib2.URLError as e:
            if tries < 10:
                print e.message
                continue
            else:
                print 'error in connecting songtaste'
                exit(0)