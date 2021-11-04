import plotly.graph_objs as go
import plotly.offline as po


def create_plot(plot_x: list, plot_y: list) -> str:
    """Creates an html string containing the bandwidth vs time graph

    :param plot_x: a list containing the timestamp points
    :type plot_x: list
    :param plot_y: a list containing the number of packets at a give timestamp point
    :type plot_y: list
    :returns: html string that is used to graph a plotly figure
    :rtype: str
    """
    # Create figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=plot_x, y=plot_y))

    # Set title
    fig.update_layout(title_text="Bandwidth vs. Time")

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

    raw_html = '<html><head><meta charset="utf-8" />'
    raw_html += '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script></head>'
    raw_html += '<body>'
    raw_html += po.plot(fig, include_plotlyjs=False, output_type='div')
    raw_html += '</body></html>'

    return raw_html
