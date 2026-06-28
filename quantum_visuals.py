"""
Quantum Visualizations for AVALYOS Dome UI
Animated quantum circuits, probability distributions, and entanglement visualizations
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from typing import List, Dict


def create_animated_quantum_circuit(title: str = "Quantum Circuit"):
    """
    Create an animated quantum circuit visualization using Plotly.
    
    Args:
        title: Chart title
    """
    # Create quantum circuit diagram
    fig = go.Figure()
    
    # Add qubit lines
    for i in range(3):
        fig.add_trace(go.Scatter(
            x=[0, 10],
            y=[i, i],
            mode='lines',
            line=dict(color='rgba(0, 212, 255, 0.5)', width=2),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # Add quantum gates (boxes with animation)
    gate_positions = [2, 5, 8]
    gate_colors = ['rgba(0, 240, 255, 0.8)', 'rgba(179, 0, 255, 0.8)', 'rgba(0, 212, 255, 0.8)']
    gate_labels = ['H', 'CNOT', 'RZ']
    
    for j, x_pos in enumerate(gate_positions):
        for i in range(3):
            fig.add_trace(go.Scatter(
                x=[x_pos - 0.3, x_pos + 0.3, x_pos + 0.3, x_pos - 0.3, x_pos - 0.3],
                y=[i - 0.2, i - 0.2, i + 0.2, i + 0.2, i - 0.2],
                mode='lines',
                fill='toself',
                fillcolor=gate_colors[j % len(gate_colors)],
                line=dict(color=gate_colors[j % len(gate_colors)], width=2),
                showlegend=False,
                hoverinfo='text',
                hovertext=gate_labels[j],
                opacity=0.7
            ))
    
    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor='center', font=dict(color='#00d4ff', size=18)),
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        paper_bgcolor='rgba(26, 31, 58, 0.3)',
        plot_bgcolor='rgba(26, 31, 58, 0)',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=300,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def create_probability_distribution(samples: List[float], title: str = "Probability Distribution"):
    """
    Create an animated probability distribution chart.
    
    Args:
        samples: List of sample values
        title: Chart title
    """
    # Create histogram with gradient
    fig = go.Figure()
    
    hist, bin_edges = np.histogram(samples, bins=20)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    fig.add_trace(go.Bar(
        x=bin_centers,
        y=hist,
        marker=dict(
            color=bin_centers,
            colorscale='Viridis',
            line=dict(color='rgba(0, 240, 255, 0.8)', width=2),
            opacity=0.8
        ),
        showlegend=False,
        hovertemplate='<b>Value:</b> %{x:.2f}<br><b>Frequency:</b> %{y}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor='center', font=dict(color='#00d4ff', size=18)),
        xaxis_title='Sample Value',
        yaxis_title='Frequency',
        hovermode='x unified',
        margin=dict(b=40, l=40, r=40, t=60),
        paper_bgcolor='rgba(26, 31, 58, 0.3)',
        plot_bgcolor='rgba(26, 31, 58, 0)',
        xaxis=dict(
            gridcolor='rgba(0, 212, 255, 0.1)',
            title_font=dict(color='#b300ff'),
            tickfont=dict(color='#00d4ff')
        ),
        yaxis=dict(
            gridcolor='rgba(0, 212, 255, 0.1)',
            title_font=dict(color='#b300ff'),
            tickfont=dict(color='#00d4ff')
        ),
        height=350
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def create_entanglement_visualization():
    """
    Create an animated entanglement visualization with connected qubits.
    """
    fig = go.Figure()
    
    # Create qubit nodes
    qubit_positions = {
        'Q0': (0, 1),
        'Q1': (1, 1),
        'Q2': (2, 1),
        'Q3': (0.5, 0),
        'Q4': (1.5, 0)
    }
    
    # Add entanglement lines
    entangled_pairs = [('Q0', 'Q1'), ('Q1', 'Q2'), ('Q2', 'Q4'), ('Q3', 'Q4')]
    
    for q1, q2 in entangled_pairs:
        x0, y0 = qubit_positions[q1]
        x1, y1 = qubit_positions[q2]
        
        fig.add_trace(go.Scatter(
            x=[x0, x1],
            y=[y0, y1],
            mode='lines',
            line=dict(color='rgba(0, 240, 255, 0.4)', width=2),
            showlegend=False,
            hoverinfo='text',
            hovertext='Entangled Pair'
        ))
    
    # Add qubit nodes
    for label, (x, y) in qubit_positions.items():
        fig.add_trace(go.Scatter(
            x=[x],
            y=[y],
            mode='markers+text',
            marker=dict(
                size=40,
                color='rgba(0, 212, 255, 0.8)',
                line=dict(color='#b300ff', width=3),
                opacity=0.9
            ),
            text=label,
            textposition='middle center',
            textfont=dict(color='#0a0e27', size=12, family='Arial Black'),
            showlegend=False,
            hovertemplate='<b>%{text}</b><extra></extra>'
        ))
    
    fig.update_layout(
        title=dict(text='Quantum Entanglement Network', x=0.5, xanchor='center', font=dict(color='#00d4ff', size=18)),
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=20, r=20, t=60),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='rgba(26, 31, 58, 0.3)',
        paper_bgcolor='rgba(26, 31, 58, 0)',
        height=400
    )
    
    fig.update_xaxes(range=[-0.5, 2.5])
    fig.update_yaxes(range=[-0.5, 1.5])
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def create_bloch_sphere():
    """
    Create a 3D Bloch sphere visualization (single qubit state).
    """
    # Create sphere
    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, np.pi, 50)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones(np.size(u)), np.cos(v))
    
    fig = go.Figure(data=[
        go.Surface(
            x=x, y=y, z=z,
            colorscale='Viridis',
            showscale=False,
            opacity=0.3,
            hoverinfo='skip'
        )
    ])
    
    # Add state vector
    theta = np.pi / 4
    phi = np.pi / 3
    
    state_x = np.sin(theta) * np.cos(phi)
    state_y = np.sin(theta) * np.sin(phi)
    state_z = np.cos(theta)
    
    fig.add_trace(go.Scatter3d(
        x=[0, state_x],
        y=[0, state_y],
        z=[0, state_z],
        mode='lines',
        line=dict(color='#00d4ff', width=5),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig.add_trace(go.Scatter3d(
        x=[state_x],
        y=[state_y],
        z=[state_z],
        mode='markers',
        marker=dict(size=8, color='#b300ff'),
        showlegend=False,
        hovertext='Qubit State',
        hoverinfo='text'
    ))
    
    fig.update_layout(
        title=dict(text='Bloch Sphere', x=0.5, xanchor='center', font=dict(color='#00d4ff', size=18)),
        scene=dict(
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            zaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            bgcolor='rgba(26, 31, 58, 0.3)'
        ),
        margin=dict(l=0, r=0, t=60, b=0),
        paper_bgcolor='rgba(26, 31, 58, 0)',
        height=500,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def create_performance_gauge(value: float, max_value: float = 100, label: str = "Performance"):
    """
    Create a glowing circular gauge chart.
    
    Args:
        value: Current value
        max_value: Maximum value for the gauge
        label: Gauge label
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title={'text': label},
        delta={'reference': max_value * 0.8},
        gauge={
            'axis': {'range': [0, max_value]},
            'bar': {'color': '#00d4ff'},
            'steps': [
                {'range': [0, max_value * 0.5], 'color': 'rgba(0, 212, 255, 0.2)'},
                {'range': [max_value * 0.5, max_value * 0.8], 'color': 'rgba(179, 0, 255, 0.2)'},
                {'range': [max_value * 0.8, max_value], 'color': 'rgba(0, 240, 255, 0.2)'}
            ],
            'threshold': {
                'line': {'color': '#b300ff', 'width': 4},
                'thickness': 0.75,
                'value': max_value * 0.9
            }
        },
        number={'font': {'color': '#00d4ff', 'size': 24}},
        title_font={'color': '#b300ff', 'size': 16}
    ))
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=80, b=20),
        paper_bgcolor='rgba(26, 31, 58, 0.3)',
        plot_bgcolor='rgba(26, 31, 58, 0)',
        font=dict(color='#00d4ff'),
        height=350
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def create_sample_distribution_3d(samples: Dict[str, int]):
    """
    Create a 3D bar chart showing sample distributions.
    
    Args:
        samples: Dictionary of category: count
    """
    categories = list(samples.keys())[:10]  # Limit to 10 categories
    values = [samples[cat] for cat in categories]
    
    fig = go.Figure(data=[
        go.Bar(
            x=categories,
            y=values,
            marker=dict(
                color=values,
                colorscale='Viridis',
                line=dict(color='#00d4ff', width=2),
                opacity=0.8
            ),
            hovertemplate='<b>%{x}</b><br>Samples: %{y}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title=dict(text='Sample Distribution', x=0.5, xanchor='center', font=dict(color='#00d4ff', size=18)),
        xaxis=dict(
            title='Category',
            gridcolor='rgba(0, 212, 255, 0.1)',
            title_font=dict(color='#b300ff'),
            tickfont=dict(color='#00d4ff')
        ),
        yaxis=dict(
            title='Count',
            gridcolor='rgba(0, 212, 255, 0.1)',
            title_font=dict(color='#b300ff'),
            tickfont=dict(color='#00d4ff')
        ),
        margin=dict(b=50, l=50, r=40, t=80),
        paper_bgcolor='rgba(26, 31, 58, 0.3)',
        plot_bgcolor='rgba(26, 31, 58, 0)',
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
