import streamlit as st
import os
import requests

import requests


import numpy as np
from stl import mesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import art3d
from mpl_toolkits.mplot3d import Axes3D

import plotly

import numpy as np
from stl import mesh  # pip install numpy-stl
import plotly.graph_objects as go
import tempfile
import os

def plot_stl_plotly(stl_filename):
    # https://chart-studio.plotly.com/~empet/15276/converting-a-stl-mesh-to-plotly-gomes/#/


    def stl2mesh3d(stl_mesh):
        # stl_mesh is read by nympy-stl from a stl file; it is  an array of faces/triangles (i.e. three 3d points) 
        # this function extracts the unique vertices and the lists I, J, K to define a Plotly mesh3d
        p, q, r = stl_mesh.vectors.shape #(p, 3, 3)
        # the array stl_mesh.vectors.reshape(p*q, r) can contain multiple copies of the same vertex;
        # extract unique vertices from all mesh triangles
        vertices, ixr = np.unique(stl_mesh.vectors.reshape(p*q, r), return_inverse=True, axis=0)
        I = np.take(ixr, [3*k for k in range(p)])
        J = np.take(ixr, [3*k+1 for k in range(p)])
        K = np.take(ixr, [3*k+2 for k in range(p)])
        return vertices, I, J, K


    my_mesh = mesh.Mesh.from_file('8teeth-gear.stl')
    
    my_mesh.vectors.shape
    
    vertices, I, J, K = stl2mesh3d(my_mesh)
    x, y, z = vertices.T
    
    colorscale= [[0, '#0a6da4'], [1, '#0a6da4']]                           
    
    mesh3D = go.Mesh3d(
                x=x,
                y=y,
                z=z, 
                i=I, 
                j=J, 
                k=K, 
                flatshading=True,
                colorscale=colorscale, 
                intensity=z, 
                name='Mesh',
                showscale=False)
    
    title = "Mesh3d from a STL"
    layout = go.Layout(paper_bgcolor='rgb(243,244,239)',
                title_text=title, title_x=0.5,
                       font_color='white',
                width=800,
                height=800,
                scene_camera=dict(eye=dict(x=1.25, y=-1.25, z=1)),
                scene_xaxis_visible=False,
                scene_yaxis_visible=False,
                scene_zaxis_visible=False)
    
    fig = go.Figure(data=[mesh3D], layout=layout)
    
    fig.data[0].update(lighting=dict(ambient= 0.18,
                                     diffuse= 1,
                                     fresnel=  .1,
                                     specular= 1,
                                     roughness= .1,
                                     facenormalsepsilon=0))
    fig.data[0].update(lightposition=dict(x=3000,
                                          y=3000,
                                          z=10000));
    
    # fig.show(renderer='browser')
    return fig


def download_file(response):
    # Надсилання GET запиту до URL
    resp_url = requests.get(response.json()['gcode_http_url'])
    
    # Перевірка на успішний відгук від сервера
    if response.json()['http_code'] == 200:
        # Запис вмісту у файл
        
        return resp_url.content
    else:
        return 0
        


def get_gcode(stl_file):


    url = "https://stl-to-g-code-slicer.p.rapidapi.com/3dslicer-02/slice"
    
    # Define the path to the STL file you want to send
    stl_file_path = stl_file  # Replace with the actual file path
    
    # Load the STL file
    files = {"stl_file": open(stl_file_path, 'rb')}
    
    payload = {
        "param": "-s roofing_monotonic=true -s roofing_layer_count=0"    
        # Add more parameters as needed without removing these two
    }
    
    headers = {"X-RapidAPI-Key": 'bf1ee2a9c2msh0bec7418b37e02ep16d6c3jsn21d5ebeba90c',
               "X-RapidAPI-Host": "stl-to-g-code-slicer.p.rapidapi.com",
    }
    
    response = requests.post(url, data=payload, files=files, headers=headers)
    
    return response 



def decode_gcode_info(gcode_binary):
    # Декодування бінарної строки
    gcode_text = gcode_binary.decode('utf-8')
    return gcode_text
 

st.set_page_config(layout="wide")

# Заголовок застосунку
st.title('STL Viewer and G-code generator')

st.sidebar.write("Оберіть налаштування для генерації G-code")


filament_diameter = st.sidebar.number_input('Діаметр філаменту', min_value=0.1, max_value=10.0, value=1.75)
layer_height = st.sidebar.number_input('Висота шару', min_value=0.01, max_value=1.0, value=0.2)
minx = st.sidebar.number_input('MINX')
miny = st.sidebar.number_input('MINY')
minz = st.sidebar.number_input('MINZ')
maxx = st.sidebar.number_input('MAXX')
maxy = st.sidebar.number_input('MAXY')
maxz = st.sidebar.number_input('MAXZ')


# Колонки для відображення діаграми та тексту
col1, col2 = st.columns(2)

with col1:
    st.header("3D View")
    # Форма для введення параметрів
    
    # Завантаження файлу STL
    uploaded_file = st.file_uploader("Upload STL file", type=['stl'])
    if uploaded_file is not None:
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(uploaded_file.getvalue())
        your_mesh = mesh.Mesh.from_file(temp_file.name)
        fig = plot_stl_plotly(your_mesh)
        st.plotly_chart(fig, use_container_width=True)
        os.unlink(temp_file.name)
        print(uploaded_file.name)
        
        resp_gcode = get_gcode(uploaded_file.name)
        gcode = download_file(resp_gcode)


        with col2:
            st.header("G-code")
            
            default_text = gcode
            default_text = decode_gcode_info(gcode)
            
            print(default_text)
            text = st.text_area("Generated G-code", value=default_text, height=500)
            
            # text = st.text_area("Enter text here", value=default_text, height=300)
            # save_button =st.download_button('Download CSV', st.text_area, 'text/csv') #st.button("Save G-code")
            st.download_button(label="Save G-code", data=text, file_name="part.gcode")
            # if save_button:
            #     filename = st.text_input("Enter filename to save text", value="example_text.txt")
            #     with open('part.gcode', 'w') as f:
            #         f.write(text)
            #     st.success("Text saved to 'saved_text.txt'")
