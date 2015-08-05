import urllib2
import urllib
import time
import re
import os
import sys
#safely urlopen url
def ULRErrorSafeURLOpen( url, maxTries = 10 ):
    for tries in range( maxTries ):
        try:
            response = urllib2.urlopen( url )
            return response
        except urllib2.URLError as e:
            if tries < maxTries:
                continue
            else:
                print ( 'error in get %s' % url )
                exit(0)
#urlretrieve callback show download processing
def callbackfunc(blocknum, blocksize, totalsize):
    percent = 100.0 * blocknum * blocksize / totalsize
    if percent > 100:
        percent = 100
    print "%.2f%%" % percent

def SafeDownloadTries( url, filePath, callback, maxTries = 10 ):
    for tries in range( maxTries ):
        try:
            urllib.urlretrieve( url, local, callbackfunc )
            return response
        except Exception as e:
            if tries < maxTries:
                continue
            else:
                print ( 'error in get %s' % url )
#songType
SongTypeDict = {
    "7d99bb4c7bd4602c342e2bb826ee8777":".wma",
    "25e4f07f5123910814d9b8f3958385ba":".Wma",
    "51bbd020689d1ce1c845a484995c0cce":".WMA",
    "b3a7a4e64bcd8aabe4cabe0e55b57af5":".mp3",
    "d82029f73bcaf052be8930f6f4247184":".MP3",
    "5fd91d90d9618feca4740ac1f2e7948f":".Mp3"
}
#in case index out of range,return default value
def getListIndex(l, index, default):
    if len(l) > index:
        return l[index]
    else:
        return default
#get realsongurl
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
        #fix
        response = urllib2.urlopen(req)
        realURL = response.read()
    return realURL
#get realsongurl
def extractSongURL( url ):
    responseL = ULRErrorSafeURLOpen(url, 10)
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

def GetUserRecSongNum( HTMLSource ):
    songNumStr1 = r'<p class="more"><a href="/user/.*?/allrec" class="underline">(.*?)</a></p>'
    songNumStr2 = r'\d\d*'
    SongNumStrList = re.findall( re.compile(songNumStr1, re.S), HTMLSource )
    songNum = 0
    if len(SongNumStrList) != 0:
        NumList = re.findall( re.compile(songNumStr2, re.S), SongNumStrList[0] )
        if len(NumList) != 0:
            songNum = int( NumList[0] )
            print "the %d user rec %d songs" % (uid, songNum)
            return songNum
    else:
    	return -1
    print "can't get songs number info"
    return songNum

def GetUserRecSongPageList( userURL ):
    userRecSongListURL = userURL + 'allrec/'
    print "get user allrec song url:%s" % userRecSongListURL
    pageStr = r"<a href='/user/.*?/allrec/(\d*)'>"
    innerRes = ULRErrorSafeURLOpen( userRecSongListURL, 10 )
    innerSrc = innerRes.read()
    pageList = re.findall( re.compile(pageStr, re.S), innerSrc )
    PageNum = 1 if len(pageList) == 0 else int( pageList[len(pageList) - 1] )
    print "the user has %d pages" % PageNum
    PageURLList = []
    for page in range(PageNum):
        realURL = userRecSongListURL + '/%d' % (page + 1)
        print "get page %d" % (page + 1)
        PageURLList.append(realURL)
    return PageURLList

def GetSongInfoInPage( pageURL ):
    response3 = ULRErrorSafeURLOpen( pageURL, 10 )
    source3 = response3.read()
    pattern = re.compile(r'WL\("(.*?)", "(.*?)","(.*?)","(.*?)"\);',re.S)
    result3 = re.findall( pattern, source3 )
    return result3

inputUserID = int(sys.argv[1])
#main process , change range number is UserID,[start,end)
for uid in range(inputUserID,inputUserID + 1):
    path = "./%d" % uid
    if not os.path.exists(path):
        os.mkdir(path)

    userURL = 'http://www.songtaste.com/user/%d/' % uid
    response =  ULRErrorSafeURLOpen( userURL, 10 )
    if response.geturl() == userURL:
        print "%s is valid" % userURL
        #extend the url to http://www.songtaste.com/user/%d/allrec/
        HTMLSource = response.read()
        #songNum
        songNum = GetUserRecSongNum( HTMLSource )
        if songNum >= 0:
            #getPageList
            PageList = GetUserRecSongPageList( userURL )
            #iterate page in user
            for pageurl in PageList:
                result3 = GetSongInfoInPage( pageurl )
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
                        SafeDownloadTries( songRealURL, local, callbackfunc )
        else:
            print "no rec songs"
    else:
        print "%s is invalid" % userURL