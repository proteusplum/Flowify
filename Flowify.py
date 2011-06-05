#! /usr/bin/env python2
def spotifylookup(uri):
	URL=u"http://ws.spotify.com/lookup/1/.json?uri="+uri
	result=simplejson.load(urllib.urlopen(URL))
	name=result["track"]["name"]
	artistnames=[]
	album=result["track"]["album"]["name"]
	for artist in result["track"]["artists"]:
		artistnames.append(artist["name"])
	
		
	isrc=""
	for id in result["track"]["external-ids"]:
		if isrc=="" and id["type"]=="isrc":
			isrc=id["id"]
	result={"title":name, "artists":artistnames, "isrc": isrc, 
"album": album}
	return result	

def isrctest(trackurn,isrc):
	URL=u"http://ws.mflow.com/DigitalDistribution.ContentCatalogue.Host.WebService/Public/Json/SyncReply/GetContent?ContentUrns="+trackurn
	trackisrc=""
	newresult=simplejson.load(urllib.urlopen(URL))
	try:
		trackisrc=newresult["Tracks"][0]["Isrc"]
	except:
		return false
	if trackisrc==isrc:
		return True
	else:
		return False
	

def mflowtracklookup(result,sessionid,userid):
	URL=u"http://ws.mflow.com/DigitalDistribution.SearchIndex.Host.WebService/Public/Json/SyncReply/SearchTracks?Query="+urllib.quote(result["title"].encode('utf-8','ignore'))+"&Take=500"
      	try:
	 displaytitle=str(result["title"])
	except: 
	 displaytitle=" "
	newresult=simplejson.load(urllib.urlopen(URL))
        flowurn=""
	artist=""
	title=""
	if newresult["TracksTotalCount"]==0:
		query=string.replace(result["title"]," - "," ")
		query=string.replace(query,")"," ")
		query=string.replace(query,"("," ")
		URL=u"http://ws.mflow.com/DigitalDistribution.SearchIndex.Host.WebService/Public/Json/SyncReply/SearchTracks?Query="+urllib.quote(query.encode('utf-8','ignore'))+"&Take=500"
		newresult=simplejson.load(urllib.urlopen(URL))
	if newresult["TracksTotalCount"]==0:
		if " - " in result["title"]:
		  try:
			query=string.rsplit(result["title"]," - ",1 )[0]
			URL=u"http://ws.mflow.com/DigitalDistribution.SearchIndex.Host.WebService/Public/Json/SyncReply/SearchTracks?Query="+urllib.quote(query.encode('utf-8','ignore'))+"&Take=500"
        		newresult=simplejson.load(urllib.urlopen(URL))
		  except:
			newresult={"Tracks": []}
	items=[]
	matches=[]
	for track in newresult["Tracks"]:
	       
               if flowurn=="":
                       result["title"] = string.replace(result["title"]," (Album Version)","")
                       result["title"] = string.replace(result["title"]," (Single Version)","")
                       result["title"] = string.replace(result["title"]," [Album Version]","")
                       result["title"] = string.replace(result["title"]," [Single Version]","")

                       track["Title"] = string.replace(track["Title"]," (Album Version)","")
                       track["Title"] = string.replace(track["Title"]," (Single Version)","")
                       track["Title"] = string.replace(track["Title"]," [Album Version]","")
                       track["Title"] = string.replace(track["Title"]," [Single Version]","")
	
                       if track["ArtistName"] in result["artists"]:
			if track["Title"].lower()==result["title"].lower(): 
			  if track["AlbumName"].lower()==result["album"].lower(): 
                                
				trackurn=track["TrackUrn"]
			  	flowurn=searchurn(trackurn)
				if flowurn=="":
					flowurn=flowit(trackurn,sessionid,userid)
				if flowurn!="":
					artist=track["ArtistName"]
					title=track["Title"]
			  else:
				matches.append(track)
			else:
				items.append(track)

        if flowurn=="":
	  if matches!=[]:
		track=matches[0]
		trackurn=track["TrackUrn"]
	  	flowurn=searchurn(trackurn)
		if flowurn=="":
			flowurn=flowit(trackurn,sessionid,userid)
		if flowurn!="":
			artist=track["ArtistName"]
			title=track["Title"]
	  if flowurn=="":
		tracklist=[]
		for item in items:
				tracklist.append(item["Title"])
		closesttitle=difflib.get_close_matches(result["title"],tracklist)
		if len(closesttitle)>1:
			for tracktitle in closesttitle:
				itempos=[i for i,x in enumerate(tracklist) if x == tracktitle]
				track=items[itempos[0]]
				trackurn=track["TrackUrn"]
				if isrctest(trackurn,result["isrc"]):
					flowurn=searchurn(trackurn)
					if flowurn=="":
						flowurn=flowit(trackurn,sessionid,userid)
					if flowurn!="":
						artist=track["ArtistName"]
						title=track["Title"]
		
		if len(closesttitle)>0 and flowurn=="":
			if len(closesttitle)>1:
				if "live" not in result["title"].lower()  and "live" in closesttitle[0]:
					closesttitle.append(closesttitle[0])
					closesttitle.pop(0)
				if "remix" not in result["title"].lower()  and "remix" in closesttitle[0]:
					closesttitle.append(closesttitle[0])
					closesttitle.pop(0)
				if "acoustic" not in result["title"].lower()  and "acoustic" in closesttitle[0]:
					closesttitle.append(closesttitle[0])
					closesttitle.pop(0)				
			itempos=[i for i,x in enumerate(tracklist) if x == closesttitle[0]]
			track=items[itempos[0]]
			trackurn=track["TrackUrn"]
			flowurn=searchurn(trackurn)
			if flowurn=="":
				flowurn=flowit(trackurn,sessionid,userid)
			if flowurn!="":
				artist=track["ArtistName"]
				title=track["Title"]
		
			
				
        output={"flowurn":flowurn, "artist":artist, "title": title} 
	return output

def flowit(trackurn, sessionid,userid):
	URL=u"http://ws.mflow.com/DigitalDistribution.UserCatalogue.Host.WebService/Public/Json/SyncReply/CreateFlowPost?ContentUrn="+trackurn+"&UserId="+userid+"&SessionId="+sessionid
	result=simplejson.load(urllib.urlopen(URL))
	if result["ResponseStatus"]["ErrorCode"]==None:
	 return result["PostUrn"]
	else:
	 return ""

def searchurn(trackurn):
	URL=u"http://ws.mflow.com/DigitalDistribution.SearchIndex.Host.WebService/Public/Json/SyncReply/SearchFlows?TrackUrns="+trackurn
	newresult=simplejson.load(urllib.urlopen(URL))
	if newresult["FlowPostsTotalCount"]!=0:
		return newresult["FlowPosts"][0]["FlowUrn"]
	else:
		return ""
	

def mflowlookup(result, sessionid, userid):
        try:
         displaytitle=str(result["title"])
        except:
	 displaytitle=""
	output=mflowtracklookup(result,sessionid,userid)
	if output["title"]=="":
		print "couldn't find " + displaytitle+ " on mFlow"
		print "#############################################"
	return output

def mflowlogin(username, password):
	userid=""
	sessionid=""
	URL=u"https://ws.mflow.com/DigitalDistribution.UserCatalogue.Host.WebService/Public/Json/SyncReply/GetLoginAuth?UserName="+username+"&Password="+password
	result=simplejson.load(urllib.urlopen(URL))
	if result["PublicSessionId"]!="00000000-0000-0000-0000-000000000000":
	 userid=result["UserId"]
	 sessionid=result["PublicSessionId"] 
	 print "successfully logged into mFlow"
	 return [userid,sessionid]
	else:
	 sys.exit("failed to log into mFlow!")

def mflowplaylist(userid, sessionid, name):
	URL=u"http://ws.mflow.com/DigitalDistribution.UserCatalogue.Host.WebService/Public/Json/SyncReply/CreateUserPlaylist?Name="+urllib.quote(name)+"&UserId="+userid+"&SessionId="+sessionid
	result=simplejson.load(urllib.urlopen(URL))
	if result["Playlist"] and result["Playlist"]["Id"]!="00000000-0000-0000-0000-000000000000":
	 print "successfully created new playlist " +name
	 return result["Playlist"]["Id"]
	else:
	 sys.exit("failed to create new playlist!")

def playlistadd(userid, sessionid, flow, playlist, oldresult):
	URL=u"http://ws.mflow.com/DigitalDistribution.UserCatalogue.Host.WebService/Public/Json/SyncReply/AddFlowToUserPlaylist?FlowId="+str(flow["flowurn"].split(":")[2])+"&SessionId="+str(sessionid)+"&UserId="+str(userid)+"&UserPlaylistId="+str(playlist)
	result=simplejson.load(urllib.urlopen(URL))
	print "Adding "+ flow["title"] +" for " +oldresult["title"]
	print "#############################################"
	return result["ResponseStatus"]["IsSuccess"]  
import simplejson
import urllib
import string
import sys
import difflib
if len(sys.argv) != 5 and len(sys.argv)!= 4:
 sys.exit("this script requires three or four arguments: mflow username, password and name of new playlist. A fourth argument can be provided giving the file containing spotify uris. If no fourth argument is provided, the contents of the clipboard will be used.")
login=mflowlogin(sys.argv[1],sys.argv[2])
userid=login[0]
sessionid=login[1]
playlist=mflowplaylist(userid,sessionid,sys.argv[3])
if len(sys.argv)==5:
 try:
  f = open(sys.argv[4], 'r')
 except: 
  sys.exit("failed to open file!")
 uris=string.split(f.read())
else:
 try:
  import pyperclip
  uris=string.split(pyperclip.getcb())
 except:
  sys.exit("failed to open file!")

counter=0
part=2
for uri in uris:
 result=spotifylookup(uri)
 flow=mflowlookup(result,sessionid,userid)
 if flow["flowurn"]!="":
	if counter==50:
		playlist=mflowplaylist(userid,sessionid,sys.argv[3]+ " pt."+str(part))
		counter=0
		part=part+1
 	if playlistadd(userid,sessionid,flow,playlist, result):
 		counter=counter+1
try:
	f.close
except: 
	pass
