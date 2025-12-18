import streamlit as st
import time
from gtts import gTTS
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Cardia AI", page_icon="💌", layout="centered")

# --- 1. DICCIONARIO DE TRADUCCIONES ---
TEXTOS = {
    "Español": {
        "titulo": "💾 Cardia IA: Generador de Tarjetas",
        "subtitulo": "Crea tarjetas con alma en segundos.",
        "sidebar_titulo": "💌 Personaliza tu Tarjeta",
        "label_idioma": "Selecciona Idioma / Select Language",
        "label_ocasion": "Ocasión",
        "opciones_ocasion": ["🎂 Cumpleaños", "💍 Bodas", "🎄 Navidad", "😔 Condolencias", "🙏 Fe"],
        "label_remitente": "Tu nombre (De parte de)",
        "label_destinatario": "Nombre del destinatario (Para)",
        "label_mensaje": "Escribe tu mensaje",
        "placeholder_mensaje": "Escribe algo bonito aquí...",
        "boton_generar": "✨ Generar Archivos",
        "spinner": "Creando magia... (Generando audio e imagen)",
        "exito": "¡Archivos listos para compartir!",
        "btn_descarga_img": "⬇️ Descargar Tarjeta (PNG)",
        "btn_descarga_audio": "⬇️ Descargar Audio (MP3)",
        "img_texto_para": "Para:",
        "img_texto_de": "De:",
        "img_texto_ocasion": "Ocasión:",
        "codigo_voz": "es" 
    },
    "English": {
        "titulo": "💾 Cardia AI: Card Generator",
        "subtitulo": "Create soulful cards in seconds.",
        "sidebar_titulo": "💌 Customize your Card",
        "label_idioma": "Select Language / Selecciona Idioma",
        "label_ocasion": "Occasion",
        "opciones_ocasion": ["🎂 Birthday", "💍 Wedding", "🎄 Christmas", "😔 Sympathy", "🙏 Faith"],
        "label_remitente": "Your Name (From)",
        "label_destinatario": "Recipient's Name (To)",
        "label_mensaje": "Write your message",
        "placeholder_mensaje": "Write something nice here...",
        "boton_generar": "✨ Generate Files",
        "spinner": "Making magic... (Generating audio and image)",
        "exito": "Files ready to share!",
        "btn_descarga_img": "⬇️ Download Card (PNG)",
        "btn_descarga_audio": "⬇️ Download Audio (MP3)",
        "img_texto_para": "To:",
        "img_texto_de": "From:",
        "img_texto_ocasion": "Occasion:",
        "codigo_voz": "en" 
    }
}

# --- 2. LÓGICA DE ESTILOS (Colores) ---
def obtener_alma(ocasion_seleccionada):
    mapa_estilos = {
        "🎂 Cumpleaños": {"color": "#FFD700", "hex": (255, 215, 0)},
        "💍 Bodas": {"color": "#FFC0CB", "hex": (255, 192, 203)},
        "🎄 Navidad": {"color": "#b22222", "hex": (178, 34, 34)},
        "😔 Condolencias": {"color": "#8e9aaf", "hex": (142, 154, 175)},
        "🙏 Fe": {"color": "#87CEEB", "hex": (135, 206, 235)},
        "🎂 Birthday": {"color": "#FFD700", "hex": (255, 215, 0)},
        "💍 Wedding": {"color": "#FFC0CB", "hex": (255, 192, 203)},
        "🎄 Christmas": {"color": "#b22222", "hex": (178, 34, 34)},
        "😔 Sympathy": {"color": "#8e9aaf", "hex": (142, 154, 175)},
        "🙏 Faith": {"color": "#87CEEB", "hex": (135, 206, 235)}
    }
    return mapa_estilos.get(ocasion_seleccionada, mapa_estilos["🎂 Cumpleaños"])

# --- 3. GENERADOR DE IMAGEN ---
def crear_imagen_descargable(ocasion, mensaje, remitente, destinatario, color_fondo, textos_idioma):
    img = Image.new('RGB', (600, 800), color=color_fondo)
    d = ImageDraw.Draw(img)
    
    try:
        font_titulo = ImageFont.truetype("arial.ttf", 40)
        font_texto = ImageFont.truetype("arial.ttf", 24)
    except:
        font_titulo = ImageFont.load_default()
        font_texto = ImageFont.load_default()

    lbl_occ = textos_idioma["img_texto_ocasion"]
    lbl_para = textos_idioma["img_texto_para"]
    lbl_de = textos_idioma["img_texto_de"]

    d.text((50, 50), f"{lbl_occ} {ocasion}", fill=(255,255,255), font=font_titulo)
    d.text((50, 150), f"{lbl_para} {destinatario}", fill=(255,255,255), font=font_titulo)
    
    margen_y = 250
    palabras = mensaje.split()
    linea_actual = ""
    for palabra in palabras:
        if len(linea_actual) + len(palabra) < 35: 
            linea_actual += palabra + " "
        else:
            d.text((50, margen_y), linea_actual, fill=(255,255,255), font=font_texto)
            margen_y += 35
            linea_actual = palabra + " "
    d.text((50, margen_y), linea_actual, fill=(255,255,255), font=font_texto)

    d.text((50, 700), f"{lbl_de} {remitente}", fill=(255,255,255), font=font_titulo)
    
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# --- INTERFAZ PRINCIPAL ---
idioma = st.sidebar.radio("🌐 Language / Idioma", ["Español", "English"])
t = TEXTOS[idioma]

st.title(t["titulo"])
st.markdown(f"*{t['subtitulo']}*")

st.sidebar.header(t["sidebar_titulo"])

ocasion = st.sidebar.selectbox(t["label_ocasion"], t["opciones_ocasion"])
remitente = st.sidebar.text_input(t["label_remitente"], "Alex")
destinatario = st.sidebar.text_input(t["label_destinatario"], "Sam")
mensaje = st.text_area(t["label_mensaje"], t["placeholder_mensaje"])

alma = obtener_alma(ocasion)

if st.button(t["boton_generar"]):
    with st.spinner(t["spinner"]):
        time.sleep(1)
        
        if idioma == "Español":
            texto_voz = f"Hola {destinatario}. {mensaje}. De parte
