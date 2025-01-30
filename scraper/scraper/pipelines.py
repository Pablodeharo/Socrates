import psycopg2
from itemadapter import ItemAdapter
from scraper.items import EscritosItem, ArgumentosItem, DialogosItem
import logging
import re

class PostgreSQLPipeline:
    def __init__(self):
        self.connection_params = {
            'host': 'localhost',
            'database': 'socrates_db',
            'user': 'postgres',
            'password': 'Pa87*blo',  
            'port': '5432',
            'client_encoding': 'UTF8'
        }
        self.connection = None
        self.cur = None

    def clean_text(self, text):
        if isinstance(text, str):
            # Reemplazar caracteres especiales
            text = text.replace('¾', 'ó')
            text = text.replace('Ý', 'í')
            text = text.replace('┐', '¿')
            text = text.replace('±', 'ñ')
            text = text.replace('ß', 'á')
            text = text.replace('\xa0', ' ')  # Eliminar espacios no rompibles
            # Eliminar espacios múltiples
            text = re.sub(r'\s+', ' ', text)
            return text.strip()
        elif isinstance(text, list):
            return [self.clean_text(item) for item in text if item and item.strip()]
        return text

    def open_spider(self, spider):
        try:
            self.connection = psycopg2.connect(**self.connection_params)
            self.cur = self.connection.cursor()
            
            # Asegurar que la conexión use UTF-8
            self.cur.execute("SET client_encoding TO 'UTF8';")
            
            # Crear tablas con codificación UTF-8
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS escritos_platon (
                    id SERIAL PRIMARY KEY,
                    titulo TEXT COLLATE "es_ES.UTF-8",
                    contenido TEXT[] COLLATE "es_ES.UTF-8"
                )
            """)
            
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS argumentos (
                    id SERIAL PRIMARY KEY,
                    titulo TEXT COLLATE "es_ES.UTF-8",
                    argumento TEXT[] COLLATE "es_ES.UTF-8"
                )
            """)
            
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS dialogos (
                    id SERIAL PRIMARY KEY,
                    titulo TEXT COLLATE "es_ES.UTF-8",
                    dialogo TEXT[] COLLATE "es_ES.UTF-8"
                )
            """)
            
            self.connection.commit()

        except psycopg2.Error as e:
            logging.error(f"Error al conectar a PostgreSQL: {e}")
            raise

    def process_item(self, item, spider):
        try:
            adapter = ItemAdapter(item)
            
            if isinstance(item, EscritosItem):
                titulo = self.clean_text(adapter.get('titulo'))
                contenido = self.clean_text(adapter.get('contenido'))
                
                self.cur.execute(
                    """INSERT INTO escritos_platon (titulo, contenido) VALUES (%s, %s)""",
                    (titulo, contenido)
                )
                
            elif isinstance(item, ArgumentosItem):
                titulo = self.clean_text(adapter.get('titulo'))
                argumento = self.clean_text(adapter.get('argumento'))
                
                self.cur.execute(
                    """INSERT INTO argumentos (titulo, argumento) VALUES (%s, %s)""",
                    (titulo, argumento)
                )
                
            elif isinstance(item, DialogosItem):
                titulo = self.clean_text(adapter.get('titulo'))
                dialogo = self.clean_text(adapter.get('dialogo'))
                
                self.cur.execute(
                    """INSERT INTO dialogos (titulo, dialogo) VALUES (%s, %s)""",
                    (titulo, dialogo)
                )
            
            self.connection.commit()
            return item

        except psycopg2.Error as e:
            logging.error(f"Error al procesar item: {e}")
            self.connection.rollback()
            raise

    def close_spider(self, spider):
        if self.cur:
            self.cur.close()
        if self.connection:
            self.connection.close()