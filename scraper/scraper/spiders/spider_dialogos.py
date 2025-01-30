import scrapy
import re
from scraper.items import DialogosItem

class SpiderDialogos(scrapy.Spider):
    name = 'spider_dialogos'
    allowed_domains = ['filosofia.org']
    start_urls = ['https://www.filosofia.org/cla/pla/azcarate.htm']

    def parse(self, response):
        # Obtener todos los enlaces que comienzan con "azc"
        enlaces = response.css('td a[href^="azc"]::attr(href)').getall()

        # Filtrar los enlaces que no contienen "argumento"
        enlaces_dialogos = [enlace for enlace in enlaces if "argumento" not in enlace]

        for enlace in enlaces_dialogos:
            url_completa = response.urljoin(enlace)
            yield scrapy.Request(url_completa, callback=self.parse_dialogos)

    def parse_dialogos(self, response):
        # Crear una instancia de DialogosItem
        item = DialogosItem()

        # Intentar extraer el título de diferentes formas
        titulo = response.css('h1.ac.c6.k5::text').get()  # Para páginas con este título
        if not titulo:
            titulo = response.css('h1.ac.c9.k1 i::text').get()  # Para páginas con el título en <i>
        
        # Si no se encuentra el título, usar otro enfoque
        if not titulo:
            titulo = response.css('i::text').get()  # Buscar título en etiquetas <i>
        
        item['titulo'] = titulo.strip() if titulo else "Título no encontrado"

        # Extraer los párrafos de texto del diálogo
        dialogos = response.css('div.c3 p, p')  # Para casos donde los diálogos estén en <div class="c3"> o en <p>
        dialogo_completo = []
        hablante_actual = None

        for dialogo in dialogos:
            # Detectar si el párrafo es un hablante
            hablante = dialogo.css('h3.ac.k5::text').get()
            if hablante:
                hablante_actual = hablante.strip()  # Guardar el hablante actual
            else:
                # Si no es un hablante, procesar el texto del diálogo
                texto = dialogo.css('::text').get()
                if texto and hablante_actual:
                    texto = re.sub(r'\[\d+\]', '', texto)  # Eliminar números entre corchetes
                    texto = texto.replace('\xa0', '').strip()  # Limpiar espacios no rompibles
                    # Formatear el diálogo como "Hablante: Texto"
                    dialogo_completo.append(f"{hablante_actual}: {texto}")
                elif texto:
                    # Si no hay hablante, agregar el texto como parte del diálogo
                    texto = texto.replace('\xa0', '').strip()  # Limpiar espacios no rompibles
                    dialogo_completo.append(f"Texto: {texto}")

        # Combinar todos los turnos de diálogo en un solo texto
        item['dialogo'] = "\n\n".join(dialogo_completo)

        yield item