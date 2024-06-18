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


#Функція для відображення STL
def plot_stl(filename):
    # Завантаження STL файлу
    your_mesh = mesh.Mesh.from_file(filename)

    # Створення нового малюнку
    figure = plt.figure()
    axes = figure.add_subplot(111, projection='3d')

    # Візуалізація мешу
    axes.add_collection3d(art3d.Poly3DCollection(your_mesh.vectors, facecolors='blue', linewidths=1, edgecolors='r', alpha=.25))

    # Масштабування графіку для відображення всієї фігури
    scale = your_mesh.points.flatten('K')
    axes.auto_scale_xyz(scale, scale, scale)

    # Показати малюнок
    plt.show()


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
    
    colorscale= [[0, '#e5dee5'], [1, '#e5dee5']]                           
    
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
                name='AT&T',
                showscale=False)
    
    title = "Mesh3d from a STL"
    layout = go.Layout(paper_bgcolor='rgb(1,1,1)',
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
    
    fig.show(renderer='browser')


def download_file(response, destination_filename):
    # Надсилання GET запиту до URL
    resp_url = requests.get(response.json()['gcode_http_url'])
    
    # Перевірка на успішний відгук від сервера
    if response.json()['http_code'] == 200:
        # Запис вмісту у файл
        with open(destination_filename, 'wb') as file:
            file.write(resp_url.content)
        print("Файл успішно завантажено.")
    else:
        print("Помилка при завантаженні файлу: ", response.status_code)


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


# Виклик функції з назвою файлу
plot_stl_plotly('8teeth-gear.stl')

resp_gcode = get_gcode('8teeth-gear.stl')

download_file(resp_gcode, '8teeth-gear.gcode')


############# plotly ##############


    
    
