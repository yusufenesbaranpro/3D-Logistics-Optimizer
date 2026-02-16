import plotly.graph_objects as go
import numpy as np
from typing import List
from packer import Bin, Item


def get_cube_mesh(item: Item, color='#CCCCCC', opacity=1.0):
    x, y, z = item.position
    dx, dy, dz = item.get_dimension()
    
    # Vertices
    X = [x, x+dx, x+dx, x, x, x+dx, x+dx, x]
    Y = [y, y, y+dy, y+dy, y, y, y+dy, y+dy]
    Z = [z, z, z, z, z+dz, z+dz, z+dz, z+dz]
    
    return go.Mesh3d(
        x=X, y=Y, z=Z,
        color=color,
        opacity=opacity,
        alphahull=0,
        flatshading=True,
        name=item.name,
        hoverinfo='name'
    ), X, Y, Z

def get_cube_wireframe(X, Y, Z, color='white'):
    # Define line segments for the cube edges
    # Bottom face: 0-1, 1-2, 2-3, 3-0
    # Top face: 4-5, 5-6, 6-7, 7-4
    # Vertical: 0-4, 1-5, 2-6, 3-7
    
    Xe = [X[0], X[1], X[2], X[3], X[0], X[4], X[5], X[6], X[7], X[4], None, X[1], X[5], None, X[2], X[6], None, X[3], X[7]]
    Ye = [Y[0], Y[1], Y[2], Y[3], Y[0], Y[4], Y[5], Y[6], Y[7], Y[4], None, Y[1], Y[5], None, Y[2], Y[6], None, Y[3], Y[7]]
    Ze = [Z[0], Z[1], Z[2], Z[3], Z[0], Z[4], Z[5], Z[6], Z[7], Z[4], None, Z[1], Z[5], None, Z[2], Z[6], None, Z[3], Z[7]]
    
    return go.Scatter3d(
        x=Xe, y=Ye, z=Ze,
        mode='lines',
        line=dict(color=color, width=2),
        hoverinfo='none',
        showlegend=False
    )

def visualize_bin(bin: Bin):
    fig = go.Figure()
    
    W, H, D = bin.width, bin.height, bin.depth
    
    # Konteyner köşe noktaları
    BX = [0, W, W, 0, 0, W, W, 0]
    BY = [0, 0, H, H, 0, 0, H, H]
    BZ = [0, 0, 0, 0, D, D, D, D]
    
    # Konteyner çerçevesi
    bin_wire = get_cube_wireframe(BX, BY, BZ, color='white')
    bin_wire.line.width = 4
    fig.add_trace(bin_wire)
    
    # Yerleştirilen kutuları çiz
    for item in bin.items:
        mesh, X, Y, Z = get_cube_mesh(item, color='#FAFAFA', opacity=0.8)
        wire = get_cube_wireframe(X, Y, Z, color='#111111')
        wire.line.width = 3
        
        fig.add_trace(mesh)
        fig.add_trace(wire)
    
    # Grafik düzeni ayarları - sadece temel özellikler kullanılıyor
    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Width', showbackground=False, showgrid=False, showline=False, zeroline=False, visible=True),
            yaxis=dict(title='Height', showbackground=False, showgrid=False, showline=False, zeroline=False, visible=True),
            zaxis=dict(title='Depth', showbackground=False, showgrid=False, showline=False, zeroline=False, visible=True),
            aspectmode='data'
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        paper_bgcolor='black',
        plot_bgcolor='black',
        font=dict(color='white')
    )
    return fig
