import scrapy
import re
from scraper.items import ArgumentosItem

class SpiderArgumentos(scrapy.Spider):
    name = 'spider_argumentos'
    allowed_domains = ['filosofia.org']
    start_urls = ['https://www.filosofia.org/cla/pla/azcarate.htm']

    def parse(self, response):
        # Extraer enlaces principales (aquellos que empiezan con 'azc')
        enlaces_argumentos = response.xpath('//td/a[starts-with(@href, "azc") and contains(text(), "argumento")]/@href').getall()

        for enlace in enlaces_argumentos:
            url_completa = response.urljoin(enlace)
            yield scrapy.Request(url_completa, callback=self.parse_argumentos)

    def parse_argumentos(self, response):
        # Crear una instancia de ArgumentosItem
        item = ArgumentosItem()

        # Extraer títulos
        titulo_principal = response.xpath('//h1[@class="ac c8 k1"]/text()').get(default='').strip()
        titulo_secundario = response.xpath('//h1[@class="ac c8 k1"]/a/i/text()').get(default='').strip()
        item['titulo'] = f"{titulo_principal} {titulo_secundario}".strip()
        
        # Extraer y limpiar argumentos
        argumentos = response.css('p:not([class])::text').getall()
        argumentos = [
            re.sub(r'\[\d+\]', '', linea)  # Elimina los números entre corchetes
            for linea in argumentos
            if not re.search(r'tomo \d+,.*\d{4},.*págs\..*', linea)
        ]
        # Eliminar espacios no rompibles (\xa0)
        item['argumento'] = [linea.replace('\xa0', '') for linea in argumentos]

        yield item