# -*- coding: utf-8 -*-

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy import Request, FormRequest

from datetime import datetime
import re

from sitebot.items import ImoOfficeItem
import json
from urllib import quote

# The site hevily use POST Requests to data transfeer.
# We need simulate the POST requst. Dict wars for The Post request.
# The settings are include the usage of the website filter.
dd = {
    'adnolist': "159223072,159373248,158836991,159422522,154966599,159418222,142789754,159340755,159341011,134281891,136456080,159339701,144709561,159414077,138724963,138349639,159312225,159373463,158740160,159352091,157095719",
    'adsource': '',
    'catid': '27_2710',
    'city': '',
    'citycheck': '',    
    'citydisp': '',    
    'cityerr': '',    
    'cityid': '0',
    'cityname': '',    
    'classtype': 'of',    
    'comm': 'all',
    'customerdisp': '',    
    'detailgeosearch': 'true',
    'dispads': '20',
    'label': '',
    'logref': '',
    'mask': 'default',
    'mode': 'search',
    'notepageno': '1',
    'only':'',
    'pageno': '1',
    'pndu': '/kleinanzeigen/cat_27_2710_ct_0_page_2.html',
    'pnno': '1',
    'pntp': '265',
    'pnur': '/immobilien/bueros-gewerbeflaechen/',
    'pnuu': '/immobilien/bueros-gewerbeflaechen/',
    'price': '',    
    'pricelow': 'von',
    'pricetop': 'bis',
    'radius': '25',
    'result': 'small',
    'search1'    : '',
    'search2'    : '',
    'searchbool': 'and',
    'searchbutton': 'true',
    'searchhelp' : '',
    'showallresults': 'false',
    'showmorecatlink': 'true',
    'sorting':'adsort',
    'suburb': '',
    'suburbid': '0',
    'tlc': '3',
    'vtlat': '0',
    'vtlong': '0',
    'zip':'',
}




def extract_city_id(value):
    """Extract city Id from JS string"""
    m = re.search("(.*)changeCity\('(.*?)'", value)
    if m:
        return m.group(2) 

def extract_url(value):
    """Extract the correct URL from js tags"""
    
    m = re.search("(.*).load\( '(.*?)'", value)
    if m:
        return m.group(2)

def json_schema_mapper(key):
    "Convert site JSON keys to our keys"
    dd = dict(title = "name",
              locationCity = "Stadt",
              locationZipCode = "PLZ",
              description = "description" ,
              priceProduct = "Kaufpreis",
              urlClick = "url",
            )
    return  dd[key]

def _normalize_price(st):
    return st
        
class ImoSpider(CrawlSpider):
    name = 'imo'
    allowed_domains = ['www.quoka.de']
    start_urls = [
                 'http://www.quoka.de/immobilien/bueros-gewerbeflaechen/'
                 ]
#  
    rules = (
        # Follow the pagination links
        Rule ( LinkExtractor(restrict_xpaths=('//ul/li/a[@class="t-pgntn-blue"]',)) ),
        # Extract items
        Rule(LinkExtractor(allow=(r'gewerbeflaechen/c', )), callback="parse_item"),  
    )
        
    def start_requests(self):
        """Override a method of the Spider.
        This is the enty Poin. See Spider Docs"""

        return [FormRequest("http://www.quoka.de/immobilien/bueros-gewerbeflaechen",
                                   formdata=dd,
                                   callback=self.set_page_filters,
                                   )]
        #
    def set_page_filters(self, response):
        """Method extract city names and city ids and start the mass crawl proccess by using
        website filters."""
        
        # get a list of city_ids
        sel = Selector(response)
        cities_by_name_selector = sel.xpath('//aside/form/div[5]/div/ul/li/ul/li/a/text()')
        cities_selector = sel.xpath('//aside/form/div[5]/div/ul/li/ul/li/a/@onclick')
        
        # create 2 lists with city ids and city names
        cities = []
        cities_by_name = []
        
        # Create a city_id list for filter    
        for city in cities_selector:
            cities.append(extract_city_id(city.extract()))
        # Create a city_name list for JS
        for city in cities_by_name_selector:
            cities_by_name.append(city.extract())    
        
        # Fetch the rest cities hidden by website   
        cities_by_name_selector_2 = sel.xpath('//div[@id="NAV_CONTENT_CITIES_MOREELEMENTS"]/ul/li/ul/li/a/text()')
        cities_selector_2 = sel.xpath('//div[@id="NAV_CONTENT_CITIES_MOREELEMENTS"]/ul/li/ul/li/a/@onclick')
        
        for city in cities_selector_2:       
            cities.append(extract_city_id(city.extract())) 
        
        for city in cities_by_name_selector_2:
            cities_by_name.append(city.extract())    
        
        
        # fetch all extern ads
        for city in cities_by_name:
            for z in range(8):
                url = "http://www.quoka.de/5U4Ope/?search=&view=quoka&platform=desktop&catid=27_2710&maxresults=50&country=D&city="+quote(city.encode('utf-8'))+"&zipcode=&suburb=&radius=25&pricemin=&pricemax=&page="+str(z) +"&gaurl=%2Foutgoing%2Fresultlist%2Fjson%2F27_2710%2Fselect%2F&output=json&kwtype=PKWSEARCHCAT&oe=UTF-8&site=searchresult&bc=0&bt=0&placement=REPLACEPLACEMENT&requesturl=http%3A%2F%2Fwww.quoka.de%2Fimmobilien%2Fbueros-gewerbeflaechen%2Fberlin%2Fcat_27_2710_ct_111756.html&analyze=1&btcid="
                yield Request(url=url,
                          callback=self.json_ads
                          )
        
        for city in cities:
            dd['cityid'] = city
            # fetch the rest
            yield FormRequest(url="http://www.quoka.de/immobilien/bueros-gewerbeflaechen/",
                    formdata=dd,
                    callback=self.parse)
            
            
#     def check(self, response):
#         f = open('today.html','w')
#         f.write(response.body)
#         f.close()
   
    def json_ads(self, response):
        jj = json.loads(response.body)
        print jj.__len__()
        for entry in jj['result']:
            item =  ImoOfficeItem()
            item['Anbieter_ID'] = 'Immobilienscout'
            item['Gewerblich'] = ''
            item['OBID'] = ''
            item['Telefon'] = ''
            item['Erstellungsdatum'] = '' 
            for k,v in entry.items():
                print k + ':' + v
                # import pdb;pdb.set_trace()
                try:
                    item[json_schema_mapper(k)] = v
                except KeyError:
                    # No problem, we don't need this value
                    pass   
            item['Kaufpreis'] = _normalize_price(item['Kaufpreis'])
            yield  item
       
           
    def parse_phone(self, response):
        #item =  ImoOfficeItem()
        item = response.meta['item']
        
        sel = Selector(response)
        #import pdb;pdb.set_trace()
        item['Telefon'] =  sel.xpath('//span/text()').extract()[0]
        self.logger.info(item)
        
        yield  item
        
    # Do not use parse method. Is the mothod of CrawSpider and is already implement.
    def parse_item(self, response):
        self.logger.info('Hi, this is an item page! %s', response.url)
        sel = Selector(response)
        # Using XPath method because more Powerful
        obj = sel.xpath('//div[@itemtype="http://data-vocabulary.org/Product"]')[0]   

        item =  ImoOfficeItem()
        
        item['Boersen_ID'] = 21
        
        #item['name'] = obj.xpath('a/text()').extract()
        #item['url'] = obj.xpath('a/@href').extract()
        #item['description'] = obj.xpath('text()').re('-\s[^\n]*\\r')
         
        item['Ueberschrift'] =  obj.xpath('//h2[@itemprop="name"]/text()').extract()[0]
        
        item['description'] = obj.xpath('//div[@itemprop="description"]/text()').extract()[0]
         
        # safe proccessor and memory
         
         
        details = obj.xpath('//div[@itemtype="http://data-vocabulary.org/Offer"]')
       
         
        item['PLZ'] =  details.xpath('//span[@class="postal-code"]/text()').extract()[0]
        item['Stadt'] = details.xpath('//span[@class="locality"]/text()').extract()[0] 
        
        item['OBID'] =  details.xpath('//div[@class="date-and-clicks"]/strong/text()').extract()[0]
       
        # '' or Immobilienscout24
        item['Anbieter_ID'] = ""



        # can be VB or float  
        # try the float as first
        
        try:
            item['Kaufpreis'] = obj.xpath('//div[@class="price has-type"]/strong/span/text()').extract()[0]  
        except IndexError:
            # try VB
            kaufpreis = obj.xpath('//div[@class="price"]/strong/text()').extract()     
            if kaufpreis:
                item['Kaufpreis'] = kaufpreis[0]
            else:
                item['Kaufpreis'] = "0"
                self.logger.info('No price %s', response.url)
          
        item['Kaufpreis'] = _normalize_price(item['Kaufpreis'])
        
        try:
            item['Gewerblich']  = obj.xpath('//div[@class="cust-type"]/text()').extract()[0]  
        except:
            item['Gewerblich'] = 'n/a'
         
        # import pdb;pdb.set_trace()
        # Can be Gestern, Heute and Defene as DE Date.
        item['erzeugt_am'] = datetime.now()
        item['Monat'] = datetime.now().strftime('%m')
        
        item['url'] = response.url
        item['Telefon'] = "" # No Phone numbers on the site
        item['Erstellungsdatum'] =  details.xpath('//div[@class="date-and-clicks"]/text()').extract()[6]
        
        item['name'] = response.url
        
        
        path=[]
        path = obj.xpath('//a[@id="dspphone1"]/@onclick')
#         if response.body.find('dspphone1')!=-1:
#             import pdb;pdb.set_trace()
        if path.__len__()>0:
            path = 'http://www.quoka.de'+extract_url(path.extract()[0]) 

            request =  Request(path, callback=self.parse_phone, meta={'item': item})
            yield request
        else:
            yield item