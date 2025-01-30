# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class EscritosItem(scrapy.Item):
    titulo = scrapy.Field()
    contenido = scrapy.Field()

class ArgumentosItem(scrapy.Item):
    titulo = scrapy.Field()
    argumento = scrapy.Field()

class DialogosItem(scrapy.Item):
    titulo = scrapy.Field()
    dialogo = scrapy.Field()
