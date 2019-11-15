'''
Copyright (c) 2019 Katana Cryptographic Ltd. All Rights Reserved.

A tool proniding a set of commands to compute statistics related to Whirpool
'''
import os
import sys
import getopt
from cmd import Cmd

# Adds whirlpool_stats directory into path
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")

from whirlpool_stats.utils.constants import ALL_DENOMS, TXID_PREFIX_LENGTH
from whirlpool_stats.utils.charts import *
from whirlpool_stats.services.downloader import Downloader
from whirlpool_stats.services.snapshot import Snapshot
from whirlpool_stats.services.forward_metrics import ForwardMetrics
from whirlpool_stats.services.backward_metrics import BackwardMetrics
from whirlpool_stats.services.tx0s_metrics import Tx0sMetrics



class WhirlpoolStats(Cmd):

  def __init__(self, working_dir, socks5):
    '''
    Constructor
    '''
    super(WhirlpoolStats, self).__init__()
    self.working_dir = working_dir
    self.socks5 = socks5
    
    # Snapshot loaded in memory
    self.snapshot = Snapshot(self.working_dir)
    # Forward looking metrics
    self.fwd_metrics = ForwardMetrics(self.snapshot)
    # Backward looking metrics
    self.bwd_metrics = BackwardMetrics(self.snapshot)
    # Tx0s metrics
    self.tx0_metrics = Tx0sMetrics(self.snapshot)


  def set_prompt(self):
    '''
    Sets the prompt
    '''
    self.prompt = 'wst#%s> ' % self.working_dir


  def do_workdir(self, args):
    '''
Displays or sets the directory storing snasphots and exported files.
Examples:
  workdir /home/whirlstats    => defines /home/whirlstats as the working directory
  workdir                     => displays the current working directory
    '''
    print('')

    if len(args) == 0:
      print(self.working_dir)
    else:
      self.working_dir = args
      self.set_prompt()

    print('')


  def do_socks5(self, args):
    '''
Displays or sets the url:port of a socks5 proxy used to download snapshots files from OXT.
Examples:
  socks5 127.0.0.1:9050    => sets the ip:port of your socks5 proxy
  socks5 none              => removes the socks5 proxy previously defined
  socks5                   => displays the current working directory
    '''
    print('')

    if len(args) == 0:
      print(self.socks5)
    elif args == 'none':
      self.socks5 = None
      print('Removed proxy.')
    else:
      self.socks5 = args
      print('Set proxy to %s.' % self.socks5)

    print(' ')


  def do_download(self, args):
    '''
Downloads the snapshot(s) for one or several pool denominations
Available denomnination codes are 05, 005, 001
Examples:
  download 05         => downloads the snapshot of the 0.5BTC pools
  download 005,001    => downloads the snapshots of the 0.05BTC and 0.01BTC pools
  download            => downloads the snapshots of all denominations
    '''
    print('')
    downloader = Downloader()
    denoms = ALL_DENOMS if (len(args) == 0) else args.split(',') 
    downloader.download(self.working_dir, denoms, self.socks5)
    print(' ')


  def do_load(self, args):
    '''
Loads in memory the snapshot of a given denomination
and computes its metrics
Available denomnination codes are 05, 005, 001
Examples:
  compute 05  => compute metrics for snaphot of the 0.5BTC pools
    '''
    print('')

    if len(args) == 0:
      print('A denomination code is mandatory.')
    elif args not in ALL_DENOMS:
      print('Invalid denomination code')
    else:
      # Loads the snapshots
      self.snapshot.set_dir(self.working_dir)
      self.snapshot.load(args)
      # Computes the metrics
      self.fwd_metrics.compute()
      self.bwd_metrics.compute()
      self.tx0_metrics.compute()

    print(' ')


  def do_score(self, args):
    '''
Displays the metrics for a mix tx identified by its txid 
Examples:
  score 450f236d596fc8a43916d624734fa7608cff1f17af5c3ddf81d7ad79021a645d
    '''
    print('')

    if len(args) == 0:
      print('The txid of a mix transaction is mandatory.')
      print(' ')
      return
    
    txid_prefix = args[0:2*TXID_PREFIX_LENGTH+1]

    if txid_prefix in self.snapshot.d_txids.keys():
      mix_round = self.snapshot.d_txids[txid_prefix]
      fwd_anonset = self.fwd_metrics.l_anonsets[mix_round]
      fwd_spread = self.fwd_metrics.l_spreads[mix_round]
      bwd_anonset = self.bwd_metrics.l_anonsets[mix_round]
      bwd_spread = self.bwd_metrics.l_spreads[mix_round]

      print('Backward-looking metrics for the outputs of this mix:')
      print('  anonset = %d' % bwd_anonset)
      print('  spread = %d%%' % bwd_spread)
      print('')
      print('Forward-looking metrics for Tx0s outputs having this transaction as their first mix:')
      print('  anonset = %d' % fwd_anonset)
      print('  spread = %d%%' % fwd_spread)

    elif txid_prefix in self.snapshot.d_tx0s.keys():
      tx0_metrics = self.tx0_metrics.d_metrics[txid_prefix]
      nb_outs = tx0_metrics[0]
      nb_counterparties = tx0_metrics[1]
      heterogeneity = float(nb_counterparties) / float(nb_outs)

      print('Metrics for this Tx0:')
      print('  number of mixed outputs = %d' % nb_outs)
      print('  number of counterparties (tx0s) = %d' % nb_counterparties)
      print('  heterogeneity ratio = %.2f' % heterogeneity)

    else:
      print('Transaction not found in this snapshot.')

    print(' ')


  def do_plot(self, args):
    '''
Plots a scatterplot for a given metrics.
Examples:
  plot fwd anonset      => plot a scatterplot displaying the forward looking anonsets (lin scale)
  plot bwd spread       => plot a scatterplot displaying the backward looking spreads (lin scale)
  plot bwd spread log   => plot a scatterplot with the y-axis in log scale
  plot act inflow       => plot a linechart of the daily inflow expressed in new incoming UTXOs
  plot act mixes        => plot a linechart of the daily number of mixes
  plot act tx0s_created => plot a linechart of the daily number of Tx0s created
  plot act tx0s_active  => plot a linechart of the daily number of active Tx0s
  plot tx0 hr           => plot a scatterplot displaying the heteogeneity ratio of the tx0s
  plot tx0 hrout        => plot a scatterplot displaying heteogeneity ratio vs #mixed outputs for the tx0s
  plot tx0 hrdist       => plot a histogram displaying the distribution of tx0s per heterogeneity ratio
    '''
    print('')

    if len(args) == 0:
      print('Category and metrics are mandatory.')
    else:
      l_args = args.split(' ')
      category = l_args[0]
      metrics = l_args[1]
      log_scale = True if ((len(l_args) == 3) and l_args[2] == 'log') else False

      # Backward/Forward looking metrics
      if category in ['fwd', 'bwd']:
        if category == 'fwd':
          o_metrics = self.fwd_metrics
          lbl_direction = 'forward-looking'
        elif category == 'bwd':
          o_metrics = self.bwd_metrics
          lbl_direction = 'backward-looking'

        if metrics == 'anonset':
          chart_type = CT_SCATTERPLOT
          y_values = o_metrics.l_anonsets
          x_values = list(range(0, len(y_values)))
          lbl_x = 'mix round'
          lbl_y = 'anonset'
          chart_title = 'Whirlpool %s %s (pools %s)' %\
            (lbl_direction, lbl_y, o_metrics.snapshot.denom)

        elif metrics == 'spread':
          chart_type = CT_SCATTERPLOT
          y_values = o_metrics.l_spreads
          x_values = list(range(0, len(y_values)))
          lbl_x = 'mix round'
          lbl_y = 'spread'
          chart_title = 'Whirlpool %s %s (pools %s)' %\
            (lbl_direction, lbl_y, o_metrics.snapshot.denom)

        else:
          print('Invalid metrics (values: anonset, spread).')

      # Tx0s metrics
      elif category == 'tx0':
        o_metrics = self.tx0_metrics
        lbl_direction = 'Tx0s counterparties heterogeneity'

        if metrics == 'hr':
          chart_type = CT_SCATTERPLOT
          l_metrics = list(o_metrics.d_metrics.values())
          y_values = [float(item[1]) / float(item[0]) for item in l_metrics]
          x_values = list(range(0, len(y_values)))
          lbl_x = 'tx0 index'
          lbl_y = 'heterogeneity ratio (#counterparties / #mixed outputs)'
          chart_title = 'Whirlpool %s (pools %s)' %\
            (lbl_direction, o_metrics.snapshot.denom)

        elif metrics == 'hrout':
          chart_type = CT_SCATTERPLOT
          l_metrics = list(o_metrics.d_metrics.values())
          y_values = [float(item[1]) / float(item[0]) for item in l_metrics]
          x_values = [item[0] for item in l_metrics]
          lbl_x = '#outputs mixed'
          lbl_y = 'heterogeneity ratio'
          chart_title = 'Whirlpool %s vs %s (pools %s)' %\
            (lbl_y, lbl_x, o_metrics.snapshot.denom)

        elif metrics == 'hrdist':
          chart_type = CT_BARCHART
          l_metrics = list(o_metrics.d_metrics.values())
          x_values = [float(item[1]) / float(item[0]) for item in l_metrics]
          lbl_x = 'heterogeneity ratio'
          lbl_y = 'percentage of all Tx0s'
          chart_title = 'Whirlpool distribution of Tx0s per %s (pools %s)' %\
            (lbl_x, o_metrics.snapshot.denom)

        else:
          print('Invalid metrics (values: hr, hrout, hrdist).')

      # Activity metrics
      elif category == 'act':
        if metrics == 'inflow':
          o_metrics = self.bwd_metrics
          chart_type = CT_LINEARCHART
          l_inflow = sorted(o_metrics.d_inflow.items())
          x_values, y_values = zip(*l_inflow)
          lbl_x = 'date'
          lbl_y = 'inflow (#UTXOs entering the pool)'
          chart_title = 'Whirlpool daily inflow (pools %s)' % o_metrics.snapshot.denom

        elif metrics == 'mixes':
          o_metrics = self.bwd_metrics
          chart_type = CT_LINEARCHART
          l_nb_mixes = sorted(o_metrics.d_nb_mixes.items())
          x_values, y_values = zip(*l_nb_mixes)
          lbl_x = 'date'
          lbl_y = 'mixes'
          chart_title = 'Whirlpool mixes (pools %s)' % o_metrics.snapshot.denom

        elif metrics == 'tx0s_active':
          o_metrics = self.bwd_metrics
          chart_type = CT_LINEARCHART
          l_nb_mixes = sorted(o_metrics.d_nb_active_tx0s.items())
          x_values, y_values = zip(*l_nb_mixes)
          lbl_x = 'date'
          lbl_y = 'active tx0s'
          chart_title = 'Whirlpool active Tx0s (pools %s)' % o_metrics.snapshot.denom

        elif metrics == 'tx0s_created':
          o_metrics = self.tx0_metrics
          chart_type = CT_LINEARCHART
          l_tx0s = sorted(o_metrics.d_nb_new_tx0s.items())
          x_values, y_values = zip(*l_tx0s)
          lbl_x = 'date'
          lbl_y = 'tx0s created'
          chart_title = 'Whirlpool Tx0s created (pools %s)' % o_metrics.snapshot.denom

        else:
          print('Invalid metrics (values: inflow, mixes, tx0s_created, tx0s_active).')

      # Unknown category
      else:
        print('Invalid category (values: fwd, bwd, act, tx0).')
        return
     
      print('Preparing the chart...')
      
      if chart_type == CT_SCATTERPLOT:
        scatterplot(x_values, y_values, log_scale, chart_title, lbl_x, lbl_y)
      elif chart_type == CT_BARCHART:
        barchart(x_values, chart_title, lbl_x, lbl_y)
      elif chart_type == CT_LINEARCHART:
        linearchart(x_values, y_values, log_scale, chart_title, lbl_x, lbl_y)

    print('')


  def do_export(self, args):
    '''
Exports the computed metrics for the active snapshot (csv format)
Files are exported in a given directory or in the working directory if none provided
Examples:
  export /tmp  => exports the results in the /tmp directory
  export       => exports the results in the working directory
    '''
    print('')
    export_dir = self.working_dir if (len(args) == 0) else args
    self.fwd_metrics.export_csv(export_dir)
    self.bwd_metrics.export_csv(export_dir)
    self.tx0_metrics.export_csv(export_dir)
    print(' ')


  def do_quit(self, args):
    ''''
Quits the program.
    '''
    print('')
    print('Good bye!')
    raise SystemExit


def usage():
  '''
  Usage message for this module
  '''
  sys.stdout.write('python wst.py [--workdir=/tmp] [--socks5=localhost:9050]\n')
  sys.stdout.write('\n\n[-w OR --target_dir] = Path of the directory that will store the snapshot files.')
  sys.stdout.write('\n\n[-s OR --socks5] = Url of the socks5 proxy to use for downloading the snapshot.')
  sys.stdout.flush()


if __name__ == '__main__':
  # Initializes the parameters
  working_dir = '/tmp'
  socks5 = None
  argv = sys.argv[1:]

  # Processes the command line arguments
  try:
    opts, args = getopt.getopt(
      argv,
      'hw:s:',
      ['help', 'workdir', 'socks5']
    )
  except getopt.GetoptError:
    usage()
    sys.exit(2)

  for opt, arg in opts:
    if opt in ('-h', '--help'):
      usage()
      sys.exit()
    elif opt in ('-w', '--workdir'):
      target_dir = arg
    elif opt in ('-s', '--socks5'):
      socks5 = arg

  wst = WhirlpoolStats(working_dir, socks5)
  wst.set_prompt()
  wst.cmdloop('Starting Whirlpool Stats Tools...\nType "help" for a list of available commands.\n')
