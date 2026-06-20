import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

class Visualizations:
    @staticmethod
    def create_bar_chart(data, x_col, y_col, title, color=None):
        """Membuat bar chart menggunakan Plotly"""
        fig = px.bar(
            data,
            x=x_col,
            y=y_col,
            title=title,
            color=color,
            text_auto=True
        )
        fig.update_layout(
            xaxis_title=x_col,
            yaxis_title=y_col,
            height=400
        )
        return fig

    @staticmethod
    def create_radar_chart(data, categories, title):
        """Membuat radar chart untuk perbandingan alternatif"""
        fig = go.Figure()
        
        for idx, row in data.iterrows():
            fig.add_trace(go.Scatterpolar(
                r=row[categories].values,
                theta=categories,
                fill='toself',
                name=idx
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 5]
                )
            ),
            title=title,
            height=400
        )
        return fig

    @staticmethod
    def create_heatmap(data, title):
        """Membuat heatmap untuk matriks perbandingan"""
        fig = px.imshow(
            data,
            title=title,
            text_auto=True,
            color_continuous_scale='RdBu_r'
        )
        fig.update_layout(height=400)
        return fig

    @staticmethod
    def create_donut_chart(data, names, values, title):
        """Membuat donut chart"""
        fig = px.pie(
            data,
            names=names,
            values=values,
            title=title,
            hole=0.3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        return fig

    @staticmethod
    def create_waterfall_chart(data, x_col, y_col, title):
        """Membuat waterfall chart"""
        fig = px.bar(
            data,
            x=x_col,
            y=y_col,
            title=title,
            text_auto=True
        )
        fig.update_layout(height=400)
        return fig

    @staticmethod
    def create_distribution_chart(data, column, title):
        """Membuat distribusi data"""
        fig = px.histogram(
            data,
            x=column,
            title=title,
            nbins=20
        )
        fig.update_layout(height=300)
        return fig

    @staticmethod
    def create_comparison_chart(data, columns, title):
        """Membuat chart perbandingan"""
        fig = go.Figure()
        
        for col in columns:
            fig.add_trace(go.Box(
                y=data[col],
                name=col
            ))
        
        fig.update_layout(
            title=title,
            height=400,
            yaxis_title='Nilai'
        )
        return fig