# -*- coding: utf-8 -*-

from scrapy.item import Item, Field


class ImoOfficeItem(Item):
    """Normaly I try to hold the attribute style as suggested in PEP.
    This style derived from spec. It's just a test Project.
    """
    
    name = Field() # Ueber
    id = Field() # 'increment!number!',
    Boersen_ID = Field() #  'website!number!(fix!=21)!',
    OBID = Field() # 'Objekt!ID!of!the!offer!on!the!website,!extract!from!detail!page!URL! or!field!„Anzeige:“!',
    erzeugt_am = Field() #  'crawling!date',
    Anbieter_ID = Field()# "Immobilienscout24\"!',
    Anbieter_ObjektID = Field()# 'empty',
    Immobilientyp = Field() # 'Büros,!Gewerbeflächen',
    Immobilientyp_detail = Field() #  NULL COMMENT 'empty',
    Vermarktungstyp = Field() # 'kaufen',
    Kaufpreis = Field()
    Land = Field() #'Deutschland',
    Bundesland = Field() # 'Empty\n',
    Bezirk = Field() #'Empty',
    Stadt = Field() # 'City',
    PLZ = Field() # 'ZIP',
    Strasse = Field() ,
    Haushnummer = Field()
    Ueberschrift = Field() # 'Title of the offer',
    description = Field() # = Beschreibung
    Wohnflaeche = Field()
    Monat = Field()
    url = Field()
    Telefon = Field()
    Erstellungsdatum = Field()
    Gewerblich = Field()
