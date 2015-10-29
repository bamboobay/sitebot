# -*- coding: utf-8 -*-

from datetime import datetime
from hashlib import md5
from scrapy import log
from twisted.enterprise import adbapi

# Below imports may be interesting for future filter methods
#from scrapy.exceptions import DropItem
#from apt.auth import update

class PersistentPipeline(object):
    """This class manage the SQL connection, insert and update data
    in MySQL Server. In large projects a mapper like SQLAlchemy would be a better solution."""
    
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbargs = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)
        return cls(dbpool)

    def process_item(self, item, spider):
        # run db query in the thread pool
        d = self.dbpool.runInteraction(self._do_upsert, item, spider)
        d.addErrback(self._handle_error, item, spider)
        # at the end return the item in case of success or failure
        d.addBoth(lambda _: item)
        # return the deferred instead the item. This makes the engine to
        # process next item (according to CONCURRENT_ITEMS setting) after this
        # operation (deferred) has finished.
        return d

    def _do_upsert(self, conn, item, spider):
        """Perform an insert or update."""
        
        guid = self._get_guid(item)
        now = datetime.utcnow().replace(microsecond=0).isoformat(' ')

        conn.execute("""SELECT EXISTS(
            SELECT 1 FROM imo_office_item WHERE guid = %s
        )""", (guid, ))
        ret = conn.fetchone()[0]

        if ret:
            # Write here all fields what you wish to update.
            # For Example you can add
            # Boersen_ID=%i, OBID=%s, erzeugt_am=%s,
#           # Anbieter_ID=%s, Immobilientyp=%s, Vermarktungstyp=%s,
#           # Land = %s, Stadt=%s, PLZ=%s, Kaufpreis=%s,
#           # Telefon=%s, Erstellungsdatum=%s, Gewerblich=%s
#           # WHERE guid=%s
            conn.execute("""
                UPDATE imo_office_item
                SET Ueberschrift=%s, Beschreibung=%s, url=%s, updated=%s
                WHERE guid =  %s
            """, (item['name'], item['description'], item['url'], now, guid))
            spider.log("Item updated in db: %s %r" % (guid, item))
        else:
            conn.execute("""
                INSERT INTO imo_office_item (guid, Ueberschrift, Beschreibung, url, updated,
                Boersen_ID, OBID, erzeugt_am, Anbieter_ID, Immobilientyp, 
                Vermarktungstyp, Land, Stadt, PLZ, Kaufpreis,
                Telefon, Erstellungsdatum, Gewerblich
                )
                VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (guid, 
                 item['name'],
                 item['description'], 
                 item['url'], 
                 now,
                 21, #item['Boersen_ID'],
                 self._normalize_OBID(item['OBID']),
                 now,
                 item['Anbieter_ID'],
                 u'Büros, Gewerbeflächen',
                 'kaufen', #Vermarktungstyp = Field() # 'kaufen',
                 'Deutschland', #Land = Field() #'Deutschland',
                 item['Stadt'], # = Field() # 'City',
                 item['PLZ'], # = Field() # 'ZIP',
                 self._normalize_price(item['Kaufpreis']), # Should be Decimal for Production
                 item['Telefon'],
                 item['Erstellungsdatum'],
                 self._normalize_gewerblich_privat(item['Gewerblich'])
                 ))
            
            spider.log("Stored on MYSQL Server: %s %r" % (guid, item))

    def _handle_error(self, failure, item, spider):
        """DB Error"""
        log.err(failure)

    def _get_guid(self, item):
        """Generates an unique identifier for a given item."""
        # Hash for future updates based on URL
        return md5(item['url']).hexdigest()

    def _normalize_price(self, st):
        try:
            st = st.replace(',00 EUR', '')
            st = st.replace('.','')
            st = st.replace(',-','')
            st = st.replace('EUR', '')
            st = st.replace(' ', '')
            st = st.replace(',', '.')
            st = st.replace('VHS', '')
            if st==u'':
                return float(0)
            return float(st)
        except:
            return float(0)
        
    def _normalize_gewerblich_privat(self, st):
        if st.strip()==u'Gewerblicher Inserent':
            return 0
        return 1
    
    def _normalize_OBID(self, st):
        try:
            return int(st)
        except:
            return 0