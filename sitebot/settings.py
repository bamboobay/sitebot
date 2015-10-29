# Scrapy settings for dirbot project

SPIDER_MODULES = ['sitebot.spiders']
NEWSPIDER_MODULE = 'sitebot.spiders'
DEFAULT_ITEM_CLASS = 'sitebot.items.ImoOfficeItem'

# Add more pipelines if you wish
ITEM_PIPELINES = {'sitebot.pipelines.PersistentPipeline': 1,
                  }

MYSQL_HOST = '127.0.0.1'
MYSQL_DBNAME = 'imocollection'
MYSQL_USER = 'imocollection'
MYSQL_PASSWD = 'test'