======
sitebot
======

This is a Scrapy project to scrape from http://www.quoka.de/immobilien/bueros-gewerbeflaechen/all items.

Items
=====

The items scraped by this project are websites, and the item is defined in the
class::

    sitebot.items.ImoOfficeItem

See the source code details.

Spiders
=======

This project contains one spider called ``imo`` that you can see by running::

    scrapy list

Spider: imo
-----------

The ``imo`` spider scrapes the site category Büros, Gewerbeflächen on http://www.quoka.de/.

You can run spider regularly (with ``scrapy crawl imo``) it will scrape the category using 
site filtest. City filter and "provide".

For Debug mode use the command scrapy crawl  --logfile=a.log -L DEBUG imo

Pipelines
=========

This project uses a pipeline to add enties to the MySQL Database. 
You need a running MySQL server on standard Ports and setup the Database.
Database Dump you will find in the var/mysql_dump Folder.

Database
========

The MySQL access settings you can find in the settings.py file.
