'''
Copyright (c) 2019 Katana Cryptographic Ltd. All Rights Reserved.

A set of function for plotting charts
'''
import plotly.graph_objects as go


'''
CONSTANTS
'''
# Chart type Scatterplot
CT_SCATTERPLOT = 0

# Chart type Barchart
CT_BARCHART = 1


def scatterplot(x_values, y_values, log_scale, chart_title, lbl_x, lbl_y):
  scatter = go.Scatter(
    x=x_values,
    y=y_values,
    mode='markers'
  )

  fig = go.Figure(data=scatter)

  font_title = dict(
    family="Courier New, monospace",
    size=18,
    color="#9f9f9f"
  )

  font_axes = dict(
    family="Courier New, monospace",
    size=13,
    color="#8f8f8f"
  )

  fig.update_traces(
    mode='markers',
    marker_size=3
  )

  fig.update_layout(
    template='plotly_dark',
    yaxis_type = 'log' if log_scale else 'linear',
    title=go.layout.Title(
      text=chart_title,
      font=font_title
    ),
    xaxis=go.layout.XAxis(
      title=go.layout.xaxis.Title(
        text=lbl_x,
        font=font_axes
      )
    ),
    yaxis=go.layout.YAxis(
      title=go.layout.yaxis.Title(
        text=lbl_y,
        font=font_axes
      )
    )
  )

  fig.show(config={
    'scrollZoom': True,
    'displayModeBar': True,
    'editable': True
  })


def barchart(x_values, chart_title, lbl_x, lbl_y):
  histo = go.Histogram(
    x=x_values,
    histnorm='percent'
  )

  fig = go.Figure(data=histo)

  font_title = dict(
    family="Courier New, monospace",
    size=18,
    color="#9f9f9f"
  )

  font_axes = dict(
    family="Courier New, monospace",
    size=13,
    color="#8f8f8f"
  )

  fig.update_layout(
    template='plotly_dark',
    title=go.layout.Title(
      text=chart_title,
      font=font_title
    ),
    xaxis=go.layout.XAxis(
      title=go.layout.xaxis.Title(
        text=lbl_x,
        font=font_axes
      )
    ),
    yaxis=go.layout.YAxis(
      title=go.layout.yaxis.Title(
        text=lbl_y,
        font=font_axes
      )
    )
  )

  fig.show(config={
    'displayModeBar': True,
    'editable': True
  })
