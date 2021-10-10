import plotly.offline as po
import plotly.graph_objs as go
import pandas as pd
from scapy.all import *
import datetime

from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5 import QtCore, QtWidgets
import sys

class Plot (): 
    def __init__(self, pcap = ''):
        self.pcap = pcap
        self.fig = None
        self.fig_view = None
        self.raw_html = None
        self.create_plot()
    
    def show_qt(self, fig):
        self.raw_html = '<html><head><meta charset="utf-8" />'
        self.raw_html += '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script></head>'
        self.raw_html += '<body>'
        self.raw_html += po.plot(fig, include_plotlyjs=False, output_type='div')
        self.raw_html += '</body></html>'
        
        if self.pcap == '':
            self.fig_view = QWebEngineView()
        # setHtml has a 2MB size limit, need to switch to setUrl on tmp file
        # for large figures.
        self.fig_view.setHtml(self.raw_html)
        #self.fig_view.show()
        #self.fig_view.raise_()

    def create_plot(self):
        # Load data
        if self.pcap != '':
            pcap = rdpcap(self.pcap)
            date, value = [], []
            for p in pcap:
                date.append(datetime.datetime.fromtimestamp(float(p.time)))

            ranges = pd.date_range(date[0].replace(microsecond=0, second=0), 
                date[-1].replace(microsecond=0, second=0, minute=date[-1].minute+1), periods = 20)
            r_val = [0 for i in range(len(ranges))]

            for d in date:
                for i in reversed(range(len(ranges))):
                    if d >= ranges[i]:
                        r_val[i] += 1
                        break;
        else:
            ranges, r_val = [datetime.date(2000,1,1), datetime.date(2001,1,1)], [0,0]

        # Create figure
        self.fig = go.Figure()
        self.fig.add_trace(go.Scatter(x=ranges, y=r_val))

        # Set title
        self.fig.update_layout(
            title_text="Bandwidth vs. Time")

        # Add range slider
        self.fig.update_layout(
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(step="all")
                    ])
                ),
                rangeslider=dict(
                    visible=True
                ),
                type="date"
            )
        )
        fig_view = self.show_qt(self.fig)
        
    def update_pcap(self, path):
        self.pcap = path
        self.create_plot()