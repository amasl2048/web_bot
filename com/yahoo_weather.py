#!/usr/bin/env python
"""
  Weather report bot
"""
import urllib2, urllib, json
import yaml
import sys
from time import asctime

def weather_report(parameter):
    '''
    parameter:
    "all" - full weather report
    "diff" - only differennce from last report
    '''
    # Check file last.yml
    try:
        f = open('./last.yml')
        prev = yaml.safe_load(f)
        f.close()
        last_file = True
    except:
        last_file = False
        print "Warning: no last file..."
                
    Moscow = '2122265'
    baseurl = "https://query.yahooapis.com/v1/public/yql?"
    yql_query = "select * from weather.forecast where woeid=" + Moscow
    yql_url = baseurl + urllib.urlencode({'q':yql_query}) + "&format=json"
    try:
      result = urllib2.urlopen(yql_url).read()
    except:
      print "Error: no connection..."
      sys.exit(0)

    def far2cel(far):
        return int( (int(far)-32)*5/9. )
      
    # Data
    data = json.loads(result)
    date = data["query"]["results"]["channel"]["item"]["forecast"][0]["date"]
    temp_h = far2cel( data["query"]["results"]["channel"]["item"]["forecast"][0]["high"] )
    temp_l = far2cel( data["query"]["results"]["channel"]["item"]["forecast"][0]["low"] )
    text = data["query"]["results"]["channel"]["item"]["forecast"][0]["text"]
    humidity =  int( data["query"]["results"]["channel"]["atmosphere"]["humidity"] )
    pressure = int( round( float( data["query"]["results"]["channel"]["atmosphere"]["pressure"] ) * 0.75 , 0 ) )
    chill = int( data["query"]["results"]["channel"]["wind"]["chill"] )
    speed = int( round(float(data["query"]["results"]["channel"]["wind"]["speed"]) * 1000 / 3600., 0))

    # Check the date
    new = False
    if (last_file):
        if (prev["date"] != date ): 
            new = True
            print "New file..."
            #sys.exit(1)

    # Caclulate difference
    diff = temp_h - temp_l
    if (last_file):
      temp_h_diff = temp_h - prev["temp_h"]
      temp_l_diff = temp_l - prev["temp_l"]
      pressure_diff = pressure - prev["pressure"]

    # Create report
    #report = "Date: '" + date + "'\n"
    report = ''

    if (last_file):
        if ( abs(temp_h_diff) > 7): report += "Temp. high diff: " + str(temp_h_diff) +\
					"(" + str(prev["temp_h"])  + " -> " +\
					str(temp_h) +  ")" + " C\n"
        if ( abs(temp_l_diff) > 7): report += "Temp. low diff: " + str(temp_l_diff) +\
 					"(" + str(prev["temp_l"])  + " -> " +\
					str(temp_l) +  ")" + " C\n"
	if ( (temp_l > 0) and (prev["temp_l"] < 0) ): report += "T low up zero:" + str(temp_l) + " C\n"
	if ( (temp_h > 0) and (prev["temp_h"] < 0) ): report += "T high up zero:" + str(temp_h) + " C\n"
	if ( (temp_l < 0) and (prev["temp_l"] > 0) ): report += "T low down zero:" + str(temp_l) + " C\n"
	if ( (temp_h < 0) and (prev["temp_h"] > 0) ): report += "T high down zero:" + str(temp_h) + " C\n"

    if ( (temp_l < 0) and (temp_h > 0) ): report += "Temp. pass zero: " + str(temp_l) + ".." + str(temp_h) + " C\n"
    if ( diff >= 15 ): report += "Temp. diff: " + str(diff) + " C " +\
				"(" + str(temp_l) + " .. "+ str(temp_h)  + ")" + "\n"

    conditions = ("Rain", "storm", "Shower")
    for cond in conditions:
    	if ( cond in text ): report += "Condition: " + text + "\n"

    if ( (humidity <= 30) or (humidity >= 95) ): report += "Humidity: " + str(humidity) + " %\n"

    if ( (pressure <= 735)  or (pressure >= 770) ): report += "Pressure: " + str(pressure) + " mmHg\n"

    if (last_file):
        if ( abs(pressure_diff) > 15 ): report += "Pressure diff: " + str(pressure_diff) + " mmHg " +\
						"(" + str(prev["pressure"]) + " -> " + str(pressure) + ")"  +\
						"\n"

    if (chill <= -10): report += "Chill: " + str(chill) + "\n"

    if (speed >= 7): report += "Wind: " + str(speed) + " m/s"

    if report:
	print asctime()
	print report

    full_report = '''---
date: %s
temp_h: %s
temp_l: %s
condition: %s
humidity: %s
pressure: %s
chill: %s
speed: %s
''' % (date, temp_h, temp_l, text, humidity, pressure, chill, speed)   
    #print full_report
    
    # update last.yml
    if (new or not last_file):
        with open("./last.yml", "w") as f:
            f.writelines(full_report)
        print "last updated"

    if (parameter == "diff"):
        out = report
    else:
        out = full_report

    return out

#print weather_report("full")
