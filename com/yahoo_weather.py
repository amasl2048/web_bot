#!/usr/bin/env python
"""
  Weather report bot
"""
import pywapi
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
                
    Moscow = 'RSXX0063'
    try:
      result = pywapi.get_weather_from_yahoo(Moscow, 'metric')
    except:
      print "Error: no connection..."
      sys.exit(0)

    # Data
    date = result['forecasts'][0]['date']
    temp_h = int(result['forecasts'][0]['high'])
    temp_l = int(result['forecasts'][0]['low'])
    text = result['forecasts'][0]['text']
    humidity = int(result["atmosphere"]["humidity"])
    pressure = int(round(float(result["atmosphere"]["pressure"]) * 0.75 , 0))
    chill = int(result['wind']['chill'])
    speed = int(round(float(result['wind']['speed']) * 1000 / 3600., 0))

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
        if ( abs(temp_h_diff) > 7): report += "Temp. high diff: " + str(temp_h_diff) + " C\n"
        if ( abs(temp_l_diff) > 7): report += "Temp. low diff: " + str(temp_l_diff) + " C\n"
	if ( (temp_l > 0) and (prev["temp_l"] < 0) ): report += "T low up zero:" + str(temp_l) + " C\n"
	if ( (temp_h > 0) and (prev["temp_h"] < 0) ): report += "T high up zero:" + str(temp_h) + " C\n"
	if ( (temp_l < 0) and (prev["temp_l"] > 0) ): report += "T low down zero:" + str(temp_l) + " C\n"
	if ( (temp_h < 0) and (prev["temp_h"] > 0) ): report += "T high down zero:" + str(temp_h) + " C\n"

    if ( (temp_l < 0) and (temp_h > 0) ): report += "Temp. pass zero: " + str(temp_l) + ".." + str(temp_h) + " C\n"
    if ( diff >= 15 ): report += "Temp. diff: " + str(diff) + " C\n"

    conditions = ("Rain", "storm", "Shower")
    for cond in conditions:
    	if ( cond in text ): report += "Condition: " + text + "\n"

    if ( (humidity <= 30) or (humidity >= 95) ): report += "Humidity: " + str(humidity) + " %\n"

    if ( (pressure <= 735)  or (pressure >= 770) ): report += "Pressure: " + str(pressure) + " mmHg\n"

    if (last_file):
        if ( abs(pressure_diff) > 15 ): report += "Pressure diff: " + str(pressure_diff) + " mmHg\n"

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
        f = file("./last.yml", "wb")
        f.writelines(full_report)
        f.close()
        print "last updated"

    if (parameter == "diff"):
        out = report
    else:
        out = full_report

    return out

#weather_report("full")
