import plotly.graph_objects as go
import numpy as np
from typing import List
from packer import Bin, Item

# Vibrant color palette for items
ITEM_COLORS = [
    '#6C63FF',  # Purple
    '#00D2FF',  # Cyan
    '#FF6B6B',  # Coral Red
    '#FFD93D',  # Golden Yellow
    '#6BCB77',  # Green
    '#FF8C42',  # Orange
    '#A855F7',  # Violet
    '#EC4899',  # Pink
    '#14B8A6',  # Teal
    '#F97316',  # Amber
    '#8B5CF6',  # Lavender
    '#06B6D4',  # Sky
    '#EF4444',  # Red
    '#22C55E',  # Emerald
    '#FACC15',  # Yellow
]


def get_cube_mesh(item: Item, color='#6C63FF', opacity=0.75):
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
        hoverinfo='name',
        hovertext=f"{item.name}<br>{dx:.0f}×{dy:.0f}×{dz:.0f}"
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
    
    # Container corner points
    BX = [0, W, W, 0, 0, W, W, 0]
    BY = [0, 0, H, H, 0, 0, H, H]
    BZ = [0, 0, 0, 0, D, D, D, D]
    
    # Container wireframe — soft blue glow
    bin_wire = get_cube_wireframe(BX, BY, BZ, color='rgba(108, 99, 255, 0.6)')
    bin_wire.line.width = 3
    fig.add_trace(bin_wire)
    
    # Draw packed items with distinct colors
    for idx, item in enumerate(bin.items):
        color = ITEM_COLORS[idx % len(ITEM_COLORS)]
        mesh, X, Y, Z = get_cube_mesh(item, color=color, opacity=0.7)
        # Slightly brighter wireframe for edge definition
        wire_color = 'rgba(255, 255, 255, 0.4)'
        wire = get_cube_wireframe(X, Y, Z, color=wire_color)
        wire.line.width = 1.5
        
        fig.add_trace(mesh)
        fig.add_trace(wire)
    
    # Layout — dark blue background matching the app theme
    fig.update_layout(
        scene=dict(
            xaxis=dict(
                title='Width',
                showbackground=True,
                backgroundcolor='rgba(15, 22, 41, 0.5)',
                showgrid=True,
                gridcolor='rgba(108, 99, 255, 0.08)',
                showline=False,
                zeroline=False,
                visible=True,
                color='#7A8599'
            ),
            yaxis=dict(
                title='Height',
                showbackground=True,
                backgroundcolor='rgba(15, 22, 41, 0.5)',
                showgrid=True,
                gridcolor='rgba(108, 99, 255, 0.08)',
                showline=False,
                zeroline=False,
                visible=True,
                color='#7A8599'
            ),
            zaxis=dict(
                title='Depth',
                showbackground=True,
                backgroundcolor='rgba(15, 22, 41, 0.5)',
                showgrid=True,
                gridcolor='rgba(108, 99, 255, 0.08)',
                showline=False,
                zeroline=False,
                visible=True,
                color='#7A8599'
            ),
            aspectmode='data'
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        paper_bgcolor='#0B1120',
        plot_bgcolor='#0B1120',
        font=dict(color='#C8D0E0', family='Inter'),
        showlegend=True,
        legend=dict(
            bgcolor='rgba(26, 35, 64, 0.7)',
            bordercolor='rgba(108, 99, 255, 0.2)',
            borderwidth=1,
            font=dict(color='#E0E6F0')
        )
    )
    return fig
