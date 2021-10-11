import plotly.offline as po
import plotly.graph_objs as go
import pandas as pd
from scapy.all import *
import datetime

from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5 import QtCore, QtWidgets
import sys

class Plot (QtWidgets.QWidget): 
  def __init__(self):
    self.create_plot()
    
  def show_qt(self, fig):
    raw_html = '<html><head><meta charset="utf-8" />'
    raw_html += '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script></head>'
    raw_html += '<body>'
    raw_html += po.plot(fig, include_plotlyjs=False, output_type='div')
    raw_html += '</body></html>'

    fig_view = QWebEngineView()
    # setHtml has a 2MB size limit, need to switch to setUrl on tmp file
    # for large figures.
    fig_view.setHtml(raw_html)
    fig_view.show()
    fig_view.raise_()
    return fig_view


  def create_plot(self):
    app = QtWidgets.QApplication(sys.argv)

    # Load data
    date, value = [], []
    pcap = rdpcap("/home/kali/Downloads/smallFlows.pcap")

    for p in pcap:
        date.append(datetime.datetime.fromtimestamp(float(p.time)))

    ranges = pd.date_range(date[0].replace(microsecond=0, second=0), 
        date[-1].replace(microsecond=0, second=0, minute=date[-1].minute+1), periods = 20)
    r_val = [0 for i in range(len(ranges))]

    for d in date:
        for i in range(len(ranges)):
            if d <= ranges[i]:
                r_val[i] += 1
                break;

    # Create figure
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(x=ranges, y=r_val))

    # Set title
    fig.update_layout(
        title_text="Bandwidth vs. Time"
    )

    # Add range slider
    fig.update_layout(
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
    fig_view = self.show_qt(fig)
    #sys.exit(app.exec_())
