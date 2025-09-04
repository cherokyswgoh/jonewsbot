import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime

TOKEN = ''
CHAT_ID = ''

HEADERS = {
    'User-Agent': 'Mozilla/5.0'
}

# La clave de los diccionarios ahora solo contiene el nombre, sin formato
MEDIOS_RSS = {
    "Euronews": "https://es.euronews.com/rss?level=theme&name=news",
    "Deia": "https://www.deia.eus/rss/section/30002",
    "El Correo": "https://www.elcorreo.com/rss/2.0/",
    "El País": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/ultimas-noticias/portada",
    "The New York Times": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "Gara": "https://www.naiz.eus/es/rss/publications/gara.rss",
    "Berria": "https://www.berria.eus/uploads/feeds/feed_berria_eu.xml"
}

MEDIOS_SCRAPING = {
    "Orain": {
        "url": "https://orain.eus",
        "selector": "h2 a"
    }
}

def obtener_titulares_rss(feed_url, cantidad=3):
    feed = feedparser.parse(feed_url)
    titulares = []
    for entry in feed.entries[:cantidad]:
        titulo = entry.title.strip() if hasattr(entry, 'title') else "Sin titular"
        enlace = entry.link.strip() if hasattr(entry, 'link') else ""
        # Usa negritas y enlaces en HTML
        titulares.append(f"<b>• {titulo}</b> <a href='{enlace}'>→</a>")
    return titulares if titulares else ["(No hay titulares disponibles)"]

def obtener_titulares_scraping(url, selector, cantidad=3):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.content, 'lxml')
        enlaces = soup.select(selector)
        titulares = []
        for e in enlaces:
            texto = e.get_text(strip=True)
            href = e.get('href')
            if texto and href and not href.startswith('#'):
                link = href if href.startswith('http') else url.rstrip('/') + '/' + href.lstrip('/')
                # Usa negritas y enlaces en HTML
                titulares.append(f"<b>• {texto}</b> <a href='{link}'>→</a>")
            if len(titulares) >= cantidad:
                break
        return titulares if titulares else ["(No hay titulares disponibles)"]
    except Exception as e:
        return [f"(Error al hacer scraping: {str(e)})"]

def obtener_clima():
    hoy = "20°C, cielo parcialmente cubierto, viento suave del norte"
    manana = "21°C, posibilidad de lluvia débil por la tarde"
    aviso = "⚠️ Aviso amarillo por viento en Bizkaia"
    return f"→ Hoy en Mungia: {hoy}\n→ Mañana: {manana}\n→ {aviso}"

def generar_mensaje():
    fecha = datetime.now().strftime('%A, %d %B %Y')
    mensaje = f"🗓️ {fecha}\n\n<b>🌦️ Pronóstico del tiempo en Mungia:</b>\n{obtener_clima()}\n\n<b>🗞️ Titulares:</b>\n"
    
    # Diccionario de colores personalizados
    colores_medios = {
        "Euronews": "#005696",       # Azul
        "Deia": "#000000",           # Negro
        "Gara": "#FF0000",           # Rojo
        "Orain": "#40E0D0",          # Turquesa
        "The New York Times": "#000000", # Negro
        "Berria": "#0000FF",         # Azul (He usado un azul estándar para distinguirlo)
        "El País": "#006400",        # Verde oscuro
        "El Correo": "#FF4500"       # Naranja rojizo
    }

    for medio, url in MEDIOS_RSS.items():
        color = colores_medios.get(medio, "#000000")
        mensaje += f"\n<i><span style='color:{color};'><b>📰 {medio}:</b></span></i>\n"
        titulares = obtener_titulares_rss(url)
        mensaje += '\n'.join(titulares) + '\n'

    for medio, datos in MEDIOS_SCRAPING.items():
        color = colores_medios.get(medio, "#000000")
        mensaje += f"\n<i><span style='color:{color};'><b>📰 {medio}:</b></span></i>\n"
        titulares = obtener_titulares_scraping(datos["url"], datos["selector"])
        mensaje += '\n'.join(titulares) + '\n'

    return dividir_mensaje(mensaje)

def dividir_mensaje(texto, limite=4000):
    partes = []
    if len(texto) <= limite:
        return [texto]
    
    while len(texto) > 0:
        if len(texto) <= limite:
            partes.append(texto)
            break
        
        corte = texto[:limite].rfind('\n')
        if corte == -1:
            corte = limite
            
        partes.append(texto[:corte])
        texto = texto[corte:]
        
    return partes

def enviar_mensaje():
    mensajes = generar_mensaje()
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    for msg in mensajes:
        payload = {
            'chat_id': CHAT_ID,
            'text': msg,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True
        }
        try:
            requests.post(url, data=payload)
        except Exception as e:
            print(f"Error al enviar un mensaje a Telegram: {e}")

enviar_mensaje()
