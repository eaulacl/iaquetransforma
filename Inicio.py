import os
import streamlit as st
from streamlit_option_menu import option_menu
import anthropic
import json
import re


css_example = '''
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css">
'''
st.write(css_example, unsafe_allow_html=True)
def tit_awesome(icon, title):
    st.markdown(
        f"""
            <h1>
                <i style="font-size:32px" class="{icon}"></i> {title}
            </h1>
        """,
        unsafe_allow_html=True
    )


from anthropic import Anthropic
def procesar_solicitud_anthropic(prompt):
    client = Anthropic()
    response = client.messages.create(
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="claude-3-haiku-20240307",
    )
    return response.content[0].text


def anthropic_stream(system, user_input):
    st.session_state['respuesta']=''
    client = anthropic.Anthropic()
    prompt_final = system + " "+user_input
    # Crea el stream usando el cliente de Anthropic
    with client.messages.stream(
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt_final}],
        model="claude-3-haiku-20240307",
    ) as stream:
        # Itera sobre cada texto que llega del stream
        for text in stream.text_stream:
            st.session_state['respuesta'] += text
            yield text

def stream_to_app(system, user_input):
    # Función que pasa el generador a Streamlit para mostrar en la aplicación
    st.write_stream(anthropic_stream(system, user_input))


def extract_number(filename):
    # Extrae el número al inicio del nombre del archivo, si existe
    match = re.search(r'^(\d+)', filename)
    return int(match.group(1)) if match else 0



# Ruta de la carpeta donde se encuentran los archivos .md


carpeta_pages = "pages"
archivo_salida = "recopilafile.txt"
exclude_files = ['requirements.txt']

# Filtra solo los archivos de capítulos de primer nivel (ignora subcapítulos)
archivos_txt = sorted(
    [archivo for archivo in os.listdir(carpeta_pages) if archivo.endswith(".txt") and '.' not in archivo.split(' ')[0]],
    key=extract_number  # Usa la función definida para extraer el número
)

# Extrae los nombres de los archivos sin la extensión para usarlos en el menú
opciones_menu = [archivo[:-4] for archivo in archivos_txt]  # Asume extensión .txt de 4 caracteres
opciones_menu.append("Asistente")  # Agrega una opción adicional para el asistente

# Define los iconos para cada opción del menú
icons = ['caret-right'] * (len(opciones_menu) - 1)  # Íconos para los capítulos
icons.append('bi-robot')  # Ícono para el asistente

# Agrega al menú al sidebar
with st.sidebar:
    selected = option_menu("Índice", opciones_menu, icons=icons, default_index=0)

# busca audios
fileaudio = f"{carpeta_pages}/{selected}.mp3"
if os.path.exists(fileaudio):
    with open(fileaudio, 'rb') as audio_file:
        audio_bytes = audio_file.read()
    st.audio(audio_bytes, format='audio/mp3', start_time=0)

# Define el archivo seleccionado y verifica si existe
# La variable selected ya está definida por la elección del menú en el sidebar
file_path = os.path.join(carpeta_pages, f"{selected}.txt")
if os.path.exists(file_path):
    # Si el archivo existe, lee y muestra su contenido
    with open(file_path, 'r', encoding='utf-8') as file_handle:
        main_text = file_handle.read()
    st.markdown(main_text)  # Muestra el contenido del capítulo principal en markdown



    # Intenta mostrar la imagen asociada al capítulo, si existe
    fileimg = os.path.join(carpeta_pages, f"{selected}.jpg")
    if os.path.exists(fileimg):
        st.image(fileimg)



    # Intenta mostrar la imagen asociada al capítulo, si existe
    fileimg = os.path.join(carpeta_pages, f"{selected}.png")
    if os.path.exists(fileimg):
        st.image(fileimg)


        sub_fileimg = os.path.join(carpeta_pages, f"{selected}.json")
        if os.path.exists(sub_fileimg):
            css_example = '''
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css">        
                '''
            st.write(css_example, unsafe_allow_html=True)

            # Cargar los datos del archivo JSON
            with open(sub_fileimg, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Título del esquema
            st.write(f"<h1>{data['titulo_esquema']}</h1>", unsafe_allow_html=True)

            # Número máximo de columnas por fila
            max_columns = 3
            total_contenidos = len(data['contenidos'])
            
            # Calcular cuántas filas se necesitan
            num_filas = (total_contenidos + max_columns - 1) // max_columns

            # Índice para acceder a los contenidos
            index = 0
            fontawesome_acumulado = ''

            # Crear las filas y columnas dinámicamente
            for _ in range(num_filas):
                columnas = st.columns(max_columns)  # Siempre crear el máximo de columnas

                # Asignar contenido a cada columna en la fila actual
                for j in range(max_columns):
                    if index < total_contenidos:
                        with columnas[j]:
                            contenido = data['contenidos'][index]

                            code = f'<div style="border-radius: 7px 7px 0px 0;padding:10px 20px; background:#FF4B4B;color:white;">{contenido["titulo_paso"]}</div>'
                            code += '<div style="margin-bottom:20px; border:1px solid #ccc; padding:10px 30px">'
                            code += f'<i class="{contenido["icono"]}" style="color:#FF4B4B;font-size:56px;text-align:center; display: block; padding:20px 0px"></i>'
                            code += f'<p style="text-align:center">{contenido["descripcion_paso"]}</p>'
                            code += '</div>'
                            
                            with st.spinner("Creando ..."):
                                st.markdown(code, unsafe_allow_html=True)
                        index += 1
                    else:
                        with columnas[j]:  # Crear columna vacía para mantener el ancho uniforme
                            st.write("")  # Se escribe algo para asegurar que la columna se crea
        




    # Busca archivos de subcapítulos para el capítulo seleccionado
    subcapitulos = [f for f in os.listdir(carpeta_pages) if f.startswith(f"{selected.split(' ')[0]}.") and f.endswith(".txt")]
    if subcapitulos:
        # Extrae los títulos de los subcapítulos para usarlos como etiquetas en las pestañas
        subcapitulo_titles = [os.path.splitext(f)[0].split(' ', 1)[1] for f in subcapitulos]
        tabs = st.tabs(subcapitulo_titles)  # Crea una pestaña por cada subcapítulo
        for tab, filename in zip(tabs, subcapitulos):
            with tab:
                sub_file_path = os.path.join(carpeta_pages, filename)
                with open(sub_file_path, 'r', encoding='utf-8') as content_file:
                    sub_content = content_file.read()
                st.write(sub_content)  # Muestra el contenido de cada subcapítulo

                # Intenta mostrar la imagen asociada al subcapítulo, si existe
                sub_fileimg = sub_file_path.replace(".txt", ".jpg")
                if os.path.exists(sub_fileimg):
                    st.image(sub_fileimg)

                sub_fileimg = sub_file_path.replace(".txt", ".png")
                if os.path.exists(sub_fileimg):
                    st.image(sub_fileimg)

                sub_fileimg = sub_file_path.replace(".txt", ".mp4")
                if os.path.exists(sub_fileimg):
                    st.video(sub_fileimg)

                sub_fileimg = sub_file_path.replace(".txt", ".json")
                if os.path.exists(sub_fileimg):
                    css_example = '''
                        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css">        
                        '''
                    st.write(css_example, unsafe_allow_html=True)

                    # Cargar los datos del archivo JSON
                    with open(sub_fileimg, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # Título del esquema
                    st.write(f"<h1>{data['titulo_esquema']}</h1>", unsafe_allow_html=True)

                    # Número máximo de columnas por fila
                    max_columns = 3
                    total_contenidos = len(data['contenidos'])
                    
                    # Calcular cuántas filas se necesitan
                    num_filas = (total_contenidos + max_columns - 1) // max_columns

                    # Índice para acceder a los contenidos
                    index = 0
                    fontawesome_acumulado = ''

                    # Crear las filas y columnas dinámicamente
                    for _ in range(num_filas):
                        columnas = st.columns(max_columns)  # Siempre crear el máximo de columnas

                        # Asignar contenido a cada columna en la fila actual
                        for j in range(max_columns):
                            if index < total_contenidos:
                                with columnas[j]:
                                    contenido = data['contenidos'][index]

                                    code = f'<div style="border-radius: 7px 7px 0px 0;padding:10px 20px; background:#FF4B4B;color:white;">{contenido["titulo_paso"]}</div>'
                                    code += '<div style="margin-bottom:20px; border:1px solid #ccc; padding:10px 30px">'
                                    code += f'<i class="{contenido["icono"]}" style="color:#FF4B4B;font-size:56px;text-align:center; display: block; padding:20px 0px"></i>'
                                    code += f'<p style="text-align:center">{contenido["descripcion_paso"]}</p>'
                                    code += '</div>'
                                    
                                    with st.spinner("Creando ..."):
                                        st.markdown(code, unsafe_allow_html=True)
                                index += 1
                            else:
                                with columnas[j]:  # Crear columna vacía para mantener el ancho uniforme
                                    st.write("")  # Se escribe algo para asegurar que la columna se crea


# Obtener la fecha de modificación del archivo de salida si existe
fecha_modificacion_archivo_salida = os.path.getmtime(archivo_salida) if os.path.exists(archivo_salida) else 0

# Revisa si algún archivo .txt en la carpeta 'pages' ha sido modificado después de la fecha de modificación del archivo de salida
debe_recrear_archivo = any(
    os.path.getmtime(os.path.join(carpeta_pages, archivo)) > fecha_modificacion_archivo_salida
    for archivo in os.listdir(carpeta_pages) if archivo.endswith(".txt")
)

# Si el archivo de salida no existe o si algún archivo .txt ha sido modificado recientemente, crea o recrea el archivo de salida
if debe_recrear_archivo:
    # Obtiene todos los archivos .txt ordenados, excluyendo el archivo de salida
    archivos_txt = sorted([
        archivo for archivo in os.listdir(carpeta_pages)
        if archivo.endswith(".txt") and archivo != archivo_salida
    ], key=extract_number)  # Aplica la función de ordenamiento por número

    # Crea y abre el archivo de salida para escritura
    with open(archivo_salida, 'w', encoding='utf-8') as archivo_compilado:
        # Recorre cada archivo de capítulo/subcapítulo y escribe su contenido al archivo de salida
        for archivo in archivos_txt:
            ruta_archivo = os.path.join(carpeta_pages, archivo)
            with open(ruta_archivo, 'r', encoding='utf-8') as contenido:
                # Escribe el título del archivo (sin la extensión .txt)
                archivo_compilado.write(f"# {os.path.splitext(archivo)[0]}\n\n")
                archivo_compilado.write(contenido.read() + "\n\n")






if selected == "Asistente":

    tit_awesome("fa-solid fa-robot", "Asistente")
    st.caption("Estoy aquí para responder preguntas sobre este libro digital")

    with open(archivo_salida, 'r', encoding='utf-8') as file_handle:
        texto_archivo_salida = file_handle.read()


    if 'respuesta' not in st.session_state:
        st.session_state['respuesta'] = ''
    if 'pregunta' not in st.session_state:
        st.session_state['pregunta'] = ''      


    with open(archivo_salida, 'r', encoding='utf-8') as file_handle:
        texto_archivo_salida = file_handle.read()

    # Asegurarse de que texto_archivo_salida tiene contenido válido
    prompt_system = f"""Utiliza el siguiente contenido para fundamentar, apoyar tus respuestas, menciona el título de la sección fuente de donde obtuviste la respuesta si es que la respuesta fue obtenida del contenido:
    {texto_archivo_salida}"""  
    if 'respuesta' not in st.session_state:
        st.session_state['respuesta'] = ''
    else:
        if st.session_state['respuesta'] != "":
            with st.chat_message("user"):
                 st.write(st.session_state['pregunta'])
            with st.chat_message("assistant"):
                 st.write(st.session_state['respuesta'])

    prompt = st.chat_input("Tu Pregunta")
    if prompt:
        st.session_state['pregunta'] = prompt
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("assistant"):
            stream_to_app(prompt_system,prompt)