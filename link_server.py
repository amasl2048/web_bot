# -*- coding: utf-8 -*-
import hashlib
import urllib2
import re
from StringIO import StringIO
import gzip
import pyelliptic, base64
import shutil, datetime
import yaml

class Link:

    def link_save(self, ymlfile, key, new_data):
        iv = pyelliptic.Cipher.gen_IV('bf-cfb')
        bi = base64.encodestring(iv)
        ctx = pyelliptic.Cipher(key, iv, 1, ciphername='bf-cfb')

        ciphertext = ctx.update(new_data.encode("utf-8"))
        ciphertext += ctx.final()
        ctext = base64.encodestring(ciphertext)

        shutil.copy2(ymlfile, ymlfile + "~")
        with open(ymlfile, "w") as f:
            f.write(bi)
            f.write(ctext) 
        return

    def link_stat(self, data):
        '''
        Return total number of records and tags list
        '''
        links = yaml.load(data)
        tags = set()
        tag_list = u""
        for key, val in links.iteritems():
            tags.add(val["tag"])
        for item in tags:
            if isinstance(item, str):
                item = unicode(item, "utf-8")
            tag_list = tag_list + " " + item
        return u"%s records with tags: %s" % (len(links.keys()), tag_list)

    def link_uniq(self, data, link_id):
        '''
        Return True if link hash is unique
        '''

        links = yaml.load(data)
        try:
            hashes = links.keys()
        except AttributeError:
            return True
        if link_id in hashes:
            return False
        return True

    def link_tag(self, data, tag):
        tag = tag.lower()
        links = yaml.load(data)
        count = 0
        report = ""
        for key, val in links.iteritems():
            if val["tag"] == tag:
                report += val["link"] + " - " + val["title"] + "\n"
                count += 1
        return u"%s--\nFound: %s records with tag %s" % (report, count, tag)

    def link_url(self, data, url):
        url = url.lower()
        links = yaml.load(data)
        count = 0
        report = ""
        for key, val in links.iteritems():
            if url in val["link"]:
                report += val["link"] + " - " + val["title"] + "\n"
                count += 1
        return u"%s--\nFound: %s records with url %s" % (report, count, url)

    def link_title(self, data, title):
        """
        Search pattern in title record
        Ignore case for cyrillic - hack with lower case
        """
        links = yaml.load(data)
        count = 0
        report = ""
        ptitle = re.compile( title.lower(), re.L | re.I) # re.I not work with cyrillic?
        for key, val in links.iteritems():
            if isinstance(val["title"], str):
                uttl = unicode(val["title"], "utf-8").lower() # hack
            else:
                uttl = val["title"].lower()
            if ptitle.search( uttl  ):
                report += val["link"] + " - " + val["title"] + "\n"
                count += 1
        return u"%s--\nFound: %s records with title %s" % (report, count, title)

    def link_search(self, data, keyword):
        report = u""
        report += self.link_url(data, keyword) + "\n"
        report += self.link_tag(data, keyword) + "\n"
        report += self.link_title(data, keyword) + "\n"
        return report

    def get_hash(self, lnk): # lnk w/o "http"
        m = hashlib.md5()
        m.update(lnk.encode("utf-8")) 
        return (m.hexdigest())[-8:] # get last 8 hex digits
    

    def link_add(self, ymlfile, key, data, link, tag):
        """
        GET page from link
        Parse charset, title
        Save data to yml file
        """

        # separate address from "http" to check unique link_id hash
        sep = r"://"
        if "http" not in link:
            lnk = link
        else:
            prefix, lnk = link.split(sep)

        today = datetime.date.today()

        link_id = self.get_hash(lnk) # get last 8 hex digits

        if not self.link_uniq(data, link_id):
            return "Sorry: duplicate link..."

        # try https before, then try http
        if "http" not in link:
            elink = link.encode("idna")
            lnk = "https://" + link
            try:
                res = urllib2.urlopen("https://" + elink, None, 3)
            except:
                lnk = "http://" + link
                try:
                    res = urllib2.urlopen("http://" + elink, None, 3)
                except:
                    return "Error url"
        else:
            elink = lnk.encode("idna")
            lnk = link # return http prefix to save
            try:
                res = urllib2.urlopen(prefix + sep + elink, None, 3)
            except:
                return "Error url"

        if res.info().get('Content-Encoding') == 'gzip':
            buf = StringIO( res.read())
            ff = gzip.GzipFile(fileobj=buf)
            fdata = ff.read()
        else:   
            fdata = res.read()

        charset = res.info().getparam("charset")
        if not charset:
            charset = "utf-8"

        pattern = re.compile("<title>(.*?)</title>", re.I)
        title1 = pattern.findall(fdata)
        if title1:
            title = pattern.findall(fdata)[0]
            utitle = unicode(title, charset)
        else:
            utitle  = ""

        record = u'''%s:
    link: "%s"
    title: "%s"
    tag: "%s"
    date: "%s"
''' % (link_id, lnk, utitle, tag, today)

        data += record

        self.link_save(ymlfile, key, data)

        return u"%s \t %s \n %s" % (lnk.lower(), utitle, self.link_stat(data))

    def link_del(self, myfile, key, data, link): 

        yaml_data = yaml.load(data)
        prefix, lnk = link.split(r"://")
        link_id = self.get_hash(lnk) # w/o http://

        if yaml_data.has_key(link_id):
            out = yaml_data.pop(link_id)
        else:
            return ""
        data = yaml.dump(yaml_data, allow_unicode=True, encoding=None, default_flow_style=False) # unicode output
        self.link_save(myfile, key, data)
        return out["link"]

