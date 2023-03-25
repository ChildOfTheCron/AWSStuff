import feedparser
import json
import asyncio
from datetime import datetime
from time import mktime


# Security Bulletin RSS feed = https://aws.amazon.com/security/security-bulletins/feed/
# What’s New RSS feed = https://aws.amazon.com/about-aws/whats-new/recent/feed/
# AWS Blog feed = https://aws.amazon.com/blogs/aws/feed/

#dict_keys(['links', 'link', 'id', 'guidislink', 'title', 'title_detail', 'summary', 'summary_detail', 'published', 'published_parsed', 'tags', 'authors', 'author', 'author_detail'])
#time.struct_time(tm_year=2023, tm_mon=3, tm_mday=22, tm_hour=17, tm_min=6, tm_sec=44, tm_wday=2, tm_yday=81, tm_isdst=0)

def normalize_date(date):
    "dd/mm/yy"
    dt = datetime.fromtimestamp(mktime(date))
    dt = dt.strftime('%d-%m-%Y')

    return dt

def normalize_time(time):
    tm = datetime.fromtimestamp(mktime(time))
    tm = tm.strftime('%H:%M:%S')

    return tm

def isNewer(date_one, date_two):
    dt_obj1 = datetime.strptime(date_one, "%d-%m-%Y")
    dt_obj2 = datetime.strptime(date_two, "%d-%m-%Y")
    if dt_obj2 > dt_obj1:
        print(date_two + " is newer than " + date_one)
        return True
    else:
        return False

def update(url):
    # use get to get data not direct key access
    feed = feedparser.parse(url)
    for entry in feed.entries:
        for x in services_list:
            for y in services_list[x]:
                name = y.get("Name")
                if name in entry.title:
                    if isNewer(y.get("Date"), normalize_date(entry.published_parsed)):
                        y["Date"] = normalize_date(entry.published_parsed)
                        y["Time"] = normalize_time(entry.published_parsed)
                        y["Summary"] = entry.title
                        print(y["Summary"])
                        print(y["Time"])
                        print(y["Date"])


def main():

    rss_urls = ["https://aws.amazon.com/blogs/aws/feed/","https://aws.amazon.com/security/security-bulletins/feed/","https://aws.amazon.com/about-aws/whats-new/recent/feed/"]
    #rss_urls = ["https://aws.amazon.com/security/security-bulletins/feed/"]
    for url in rss_urls:
        update(url)

if __name__ == "__main__":

    services_list = []
    with open('services.json', "r") as json_file:
        services_list = json.load(json_file)

    main()

    with open('services.json', "w") as json_file:
        json.dump(services_list, json_file)


