'''
Copyright (c) 2019 Katana Cryptographic Ltd. All Rights Reserved.

A class allowing to plot metrics
'''
from whirlpool_stats.utils.charts import *


class Plotter(object):

  def __init__(self, fwd_metrics, bwd_metrics, tx0_metrics):
    '''
    Constructor
    Parameters:
      fwd_metrics = Forward-looking metrics
      bwd_metrics = Backward-looking metrics
      tx0_metrics = Tx0s metrics
    '''
    self.fwd_metrics = fwd_metrics
    self.bwd_metrics = bwd_metrics
    self.tx0_metrics = tx0_metrics


  def plot(self, category, metrics, log_scale):
    '''
    Plots a metrics identified by a category and a name
    Parameters:
      category  = category
      metrics   = name
      log_scale = flag indicating if z-axis should use a log scale
    '''
    # Backward/Forward looking metrics
    if category in ['fwd', 'bwd']:
      if category == 'fwd':
        o_metrics = self.fwd_metrics
        lbl_direction = 'forward-looking'
      elif category == 'bwd':
        o_metrics = self.bwd_metrics
        lbl_direction = 'backward-looking'

      # Anonset
      if metrics == 'anonset':
        chart_type = CT_SCATTERPLOT
        y_values = o_metrics.l_anonsets
        x_values = list(range(0, len(y_values)))
        lbl_x = 'mix round'
        lbl_y = 'anonset'
        chart_title = 'Whirlpool %s %s (pools %s)' %\
          (lbl_direction, lbl_y, o_metrics.snapshot.denom)

      # Spread
      elif metrics == 'spread':
        chart_type = CT_SCATTERPLOT
        y_values = o_metrics.l_spreads
        x_values = list(range(0, len(y_values)))
        lbl_x = 'mix round'
        lbl_y = 'spread'
        chart_title = 'Whirlpool %s %s (pools %s)' %\
          (lbl_direction, lbl_y, o_metrics.snapshot.denom)
      # Invalid name
      else:
        print('Invalid metrics (values: anonset, spread).')
        return


    # Tx0s metrics
    elif category == 'tx0':
      o_metrics = self.tx0_metrics
      lbl_direction = 'Tx0s counterparties heterogeneity'

      # Heterogeneity ratio
      if metrics == 'hr':
        chart_type = CT_SCATTERPLOT
        l_metrics = list(o_metrics.d_metrics.values())
        y_values = [float(item[1]) / float(item[0]) for item in l_metrics]
        x_values = list(range(0, len(y_values)))
        lbl_x = 'tx0 index'
        lbl_y = 'heterogeneity ratio (#counterparties / #mixed outputs)'
        chart_title = 'Whirlpool %s (pools %s)' %\
          (lbl_direction, o_metrics.snapshot.denom)

      # Heterogeneity ratio VS number of mixed Tx0s outputs
      elif metrics == 'hrout':
        chart_type = CT_SCATTERPLOT
        l_metrics = list(o_metrics.d_metrics.values())
        y_values = [float(item[1]) / float(item[0]) for item in l_metrics]
        x_values = [item[0] for item in l_metrics]
        lbl_x = '#outputs mixed'
        lbl_y = 'heterogeneity ratio'
        chart_title = 'Whirlpool %s vs %s (pools %s)' %\
          (lbl_y, lbl_x, o_metrics.snapshot.denom)

      # Distribution of Tx0s per heterogeneity ratio
      elif metrics == 'hrdist':
        chart_type = CT_BARCHART
        l_metrics = list(o_metrics.d_metrics.values())
        x_values = [float(item[1]) / float(item[0]) for item in l_metrics]
        lbl_x = 'heterogeneity ratio'
        lbl_y = 'percentage of all Tx0s'
        chart_title = 'Whirlpool distribution of Tx0s per %s (pools %s)' %\
          (lbl_x, o_metrics.snapshot.denom)

      # Invalid name
      else:
        print('Invalid metrics (values: hr, hrout, hrdist).')
        return


    # Activity metrics
    elif category == 'act':
      # Daily inflow
      if metrics == 'inflow':
        o_metrics = self.bwd_metrics
        chart_type = CT_LINEARCHART
        l_inflow = sorted(o_metrics.d_inflow.items())
        x_values, y_values = zip(*l_inflow)
        lbl_x = 'date'
        lbl_y = 'inflow (#UTXOs entering the pool)'
        chart_title = 'Whirlpool daily inflow (pools %s)' % o_metrics.snapshot.denom

      # Daily number of mixes
      elif metrics == 'mixes':
        o_metrics = self.bwd_metrics
        chart_type = CT_LINEARCHART
        l_nb_mixes = sorted(o_metrics.d_nb_mixes.items())
        x_values, y_values = zip(*l_nb_mixes)
        lbl_x = 'date'
        lbl_y = 'mixes'
        chart_title = 'Whirlpool mixes (pools %s)' % o_metrics.snapshot.denom

      # Daily number of active Tx0s
      elif metrics == 'tx0s_active':
        o_metrics = self.bwd_metrics
        chart_type = CT_LINEARCHART
        l_nb_mixes = sorted(o_metrics.d_nb_active_tx0s.items())
        x_values, y_values = zip(*l_nb_mixes)
        lbl_x = 'date'
        lbl_y = 'active tx0s'
        chart_title = 'Whirlpool active Tx0s (pools %s)' % o_metrics.snapshot.denom

      # Daily number of created Tx0s
      elif metrics == 'tx0s_created':
        o_metrics = self.tx0_metrics
        chart_type = CT_LINEARCHART
        l_tx0s = sorted(o_metrics.d_nb_new_tx0s.items())
        x_values, y_values = zip(*l_tx0s)
        lbl_x = 'date'
        lbl_y = 'tx0s created'
        chart_title = 'Whirlpool Tx0s created (pools %s)' % o_metrics.snapshot.denom

      # Invalid name
      else:
        print('Invalid metrics (values: inflow, mixes, tx0s_created, tx0s_active).')
        return


    # Unknown category
    else:
      print('Invalid category (values: fwd, bwd, act, tx0).')
      return


    print('Preparing the chart...')
    
    # Plots the chart
    if chart_type == CT_SCATTERPLOT:
      scatterplot(x_values, y_values, log_scale, chart_title, lbl_x, lbl_y)
    elif chart_type == CT_BARCHART:
      barchart(x_values, chart_title, lbl_x, lbl_y)
    elif chart_type == CT_LINEARCHART:
      linearchart(x_values, y_values, log_scale, chart_title, lbl_x, lbl_y)
