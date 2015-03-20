#!/usr/bin/env python
"""
  Weather report bot
"""
import pywapi
import yaml
import sys

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

    if ( diff > 10 ): report += "Temp. diff: " + str(diff) + " C\n"

    if ( "Rain" in text ): report += "Condition: " + text + "\n"

    if ( (humidity < 20) or (humidity > 90) ): report += "Humidity: " + str(humidity) + " %\n"

    if ( (pressure < 735)  or (pressure > 765) ): report += "Pressure: " + str(pressure) + " mmHg\n"

    if (last_file):
        if ( abs(pressure_diff) > 15 ): report += "Pressure diff: " + str(pressure_diff) + " mmHg\n"

    if (chill < -5): report += "Chill: " + str(chill) + "\n"

    if (speed >= 10): report += "Wind: " + str(speed) + " m/s"

    #print report

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

#weather_report("diff")
