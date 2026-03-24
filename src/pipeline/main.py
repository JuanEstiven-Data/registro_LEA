import logging

# Configuración del formato del logging
formato_pro = '%(asctime)s | %(filename)s:%(lineno)d | %(funcName)s() | %(levelname)s | %(message)s'
logging.basicConfig(
    level=logging.INFO, 
    format=formato_pro, # 👈 Aplicamos el nuevo formato aquí
    handlers=[
        logging.FileHandler("errores_proyecto.log", encoding='utf-8')
    ]
)