import streamlit as st
import time
from gtts import gTTS
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Cardia AI", page_icon="💌", layout="centered")

# --- 1. DICCIONARIO DE IDIOMAS ---
TEXTOS = {
    "Español": {
        "titulo": "💌 Cardia AI",
        "subtitulo": "Generador de Tarjetas con Alma",
        "sidebar_tit": "Personaliza tu mensaje",
        "idioma": "Idioma / Language",
        "ocasion": "Ocasión",
        "opciones_ocasion": ["Cumpleaños", "Bodas", "Navidad", "Condolencias", "Fe", "Amor"],
        "de": "Tu nombre (De parte de):",
        "para": "Destinatario (Para):",
        "mensaje": "Mensaje especial:",
        "boton": "✨ Crear Tarjeta Mágica",
        "spinner": "Generando voz y diseño...",
        "exito": "¡Tu tarjeta ha sido creada!",
        "desc_img": "Descargar Tarjeta (PNG)",
        "desc_audio": "Descargar Audio (MP3)",
        "voz_code": "es",
        "msg_ejemplo": "Te deseo un día lleno de alegría."
    },
    "English": {
        "titulo": "💌 Cardia AI",
        "subtitulo": "Soulful Card Generator",
        "sidebar_tit": "Customize your message",
        "idioma": "Select Language",
        "ocasion": "Occasion",
        "opciones_ocasion": ["Birthday", "Wedding", "Christmas", "Sympathy", "Faith", "Love"],
        "de": "Your Name (From):",
        "para": "Recipient (To):",
        "mensaje": "Special Message:",
        "boton": "✨ Create Magic Card",
        "spinner": "Generating voice and design...",
        "exito": "Your card has been created!",
        "desc_img": "Download Card (PNG)",
        "desc_audio": "Download Audio (MP3)",
        "voz_code": "en",
        "msg_ejemplo": "Wishing you a day full of joy."
    }
}

# --- 2. LÓGICA DE COLORES ("EL ALMA") ---
def obtener_color_fondo(ocasion_texto):
    # Diccionario de colores según la palabra clave
    if "Cumpleaños" in ocasion_texto or "Birthday" in ocasion_texto:
        return (255, 223, 186) # Durazno pastel
    elif "Bodas" in ocasion_texto or "Wedding" in ocasion_texto:
        return (255, 240, 245) # Lavanda/Rosa muy claro
    elif "Navidad" in ocasion_texto or "Christmas" in ocasion_texto:
        return (200, 50, 50) # Rojo Navidad
    elif "Condolencias" in ocasion_texto or "Sympathy" in ocasion_texto:
        return (220, 220, 220) # Gris respetuoso
    elif "Fe" in ocasion_texto or "Faith" in ocasion_texto:
        return (224, 255, 255) # Celeste cielo
    elif "Amor" in ocasion_texto or "Love" in ocasion_texto:
        return (255, 182, 193) # Rosa Amor
    else:
        return (255, 255, 255) # Blanco por defecto

# --- 3. GENERADOR DE IMAGEN ---
def generar_imagen_tarjeta(ocasion, de, para, mensaje, textos_ui):
    # Obtener color según la ocasión
    color_bg = obtener_color_fondo(ocasion)
    
    # Crear lienzo (600x600 px)
    img = Image.new('RGB', (600, 600), color=color_bg)
    d = ImageDraw.Draw(img)
    
    # Intentar cargar fuente por defecto
    try:
        fnt_grande = ImageFont.load_default()
        fnt_mediana = ImageFont.load_default()
    except:
        fnt_grande = ImageFont.load_default()
        fnt_mediana = ImageFont.load_default()

    # Color del texto (Blanco para fondos oscuros como Navidad, Negro para el resto)
    if color_bg == (200, 50, 50): # Si es rojo navidad
        fill_color = (255, 255, 255)
    else:
        fill_color = (0, 0, 0)

    # Dibujar textos (Posiciones fijas para evitar errores)
    # Título (Ocasión)
    d.text((50, 50), f"~ {ocasion} ~", font=fnt_grande, fill=fill_color)
    
    # Para
    d.text((50, 120), f"{textos_ui['para']} {para}", font=fnt_mediana, fill=fill_color)
    
    # Mensaje (Dividimos el texto si es muy largo visualmente - simple)
    # Aquí imprimimos el mensaje en el centro
    d.text((50, 200), mensaje, font=fnt_mediana, fill=fill_color)
    
    # De
    d.text((50, 500), f"{textos_ui['de']} {de}", font=fnt_mediana, fill=fill_color)
    
    # Guardar en memoria
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# --- INTERFAZ PRINCIPAL ---
idioma_sel = st.sidebar.radio("🌐", ["Español", "English"], horizontal=True)
t = TEXTOS[idioma_sel]

st.title(t["titulo"])
st.markdown(f"*{t['subtitulo']}*")
st.markdown("---")

# Barra lateral
st.sidebar.header(t["sidebar_tit"])
ocasion_input = st.sidebar.selectbox(t["ocasion"], t["opciones_ocasion"])
remitente_input = st.sidebar.text_input(t["de"], "Alex")
destinatario_input = st.sidebar.text_input(t["para"], "Sam")
mensaje_input = st.text_area(t["mensaje"], t["msg_ejemplo"])

# Botón de acción
if st.button(t["boton"], type="primary"):
    with st.spinner(t["spinner"]):
        time.sleep(1) # Pequeña pausa dramática
        
        # 1. Lógica de Audio (Texto a Voz)
        # Construimos el texto de forma segura para evitar errores de sintaxis
        if idioma_sel == "Español":
            texto_para_leer = f"Hola {destinatario_input}. {mensaje_input}. De parte de {remitente_input}."
        else:
            texto_para_leer = f"Hi {destinatario_input}. {mensaje_input}. From {remitente_input}."
            
        tts = gTTS(text=texto_para_leer, lang=t["voz_code"])
        audio_io = BytesIO()
        tts.write_to_fp(audio_io)
        
        # 2. Lógica de Imagen
        img_data = generar_imagen_tarjeta(ocasion_input, remitente_input, destinatario_input, mensaje_input, t)
        
        # 3. Mostrar Resultados
        st.success(t["exito"])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(img_data, caption=f"Tarjeta de {ocasion_input}")
            st.download_button(t["desc_img"], img_data, "tarjeta_cardia.png", "image/png")
            
        with col2:
            st.audio(audio_io, format='audio/mp3')
            st.download_button(t["desc_audio"], audio_io, "mensaje_cardia.mp3", "audio/mpeg")
