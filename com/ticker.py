import requests
import yaml

def ticker_cmd(key):
    try:
        config = yaml.load(open("/etc/bot.config"))
        api = config["ticker"]["api"] 
        tickers = config["ticker"]["tickers"]
    except:
        return "Bad config file"
        
    report = ''
    report_all = ''
    for tic in tickers:

        url = api + tic
        r = requests.get(url)

        if r.status_code == 200:

            if key == 'change':

                if abs(r.json()[0]['percent_change_24h']) >= config['ticker']['lim_24h'] or \
                    abs(r.json()[0]['percent_change_7d']) >= config['ticker']['lim_7d']:
                    report += '''%s
    %s usd
    %s%% 24h
    %s%% 7d
''' %  (r.json()[0]['symbol'],
                r.json()[0]['price_usd'],
                r.json()[0]['percent_change_24h'],
                r.json()[0]['percent_change_7d'])

            else:
                 report_all += '''%s
    %s usd
    %s%% 24h
    %s%% 7d
''' %  (r.json()[0]['symbol'],
            r.json()[0]['price_usd'],
            r.json()[0]['percent_change_24h'],
            r.json()[0]['percent_change_7d'])

        else:
            return r.status_code

    if key == "change":
        return report
    else:
        return report_all

#print ticker_cmd("change")
