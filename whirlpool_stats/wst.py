'''
Copyright (c) 2019 Katana Cryptographic Ltd. All Rights Reserved.

A tool proniding a set of commands to compute statistics related to Whirpool
'''
import os
import sys
import getopt
from cmd import Cmd
import plotly.graph_objects as go

# Adds whirlpool_stats directory into path
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")

from whirlpool_stats.utils.constants import ALL_DENOMS
from whirlpool_stats.services.downloader import Downloader
from whirlpool_stats.services.snapshot import Snapshot
from whirlpool_stats.services.forward_metrics import ForwardMetrics
from whirlpool_stats.services.backward_metrics import BackwardMetrics



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
    elif args not in self.snapshot.d_txids.keys():
      print('Transaction not found in this snapshot.')
    else:
      mix_round = self.snapshot.d_txids[args]
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

    print(' ')


  def do_plot(self, args):
    '''
Plots a scatterplot for a given metrics.
Examples:
  plot fwd anonset    => plot a scatterplot displaying the forward looking anonsets (lin scale)
  plot bwd spread     => plot a scatterplot displaying the backward looking spreads (lin scale)
  plot bwd spread log => plot a scatterplot with the y-axis in log scale
    '''
    print('')

    if len(args) == 0:
      print('Direction and metrics are mandatory.')
    else:
      l_args = args.split(' ')
      direction = l_args[0]
      metrics = l_args[1]
      log_scale = True if ((len(l_args) == 3) and l_args[2] == 'log') else False

      if direction not in ['fwd', 'bwd']:
        print('Invalid direction (values: fwd, bwd).')
      elif metrics not in ['anonset', 'spread']:
        print('Invalid metrics (values: anonset, spread).')
      else:
        if direction == 'fwd':
          o_metrics = self.fwd_metrics
          lbl_direction = 'forward-looking'
        else:
          o_metrics = self.bwd_metrics
          lbl_direction = 'backward-looking'

        if metrics == 'anonset':
          l_metrics = o_metrics.l_anonsets
          lbl_metrics = 'anonset'
        else:
          l_metrics = o_metrics.l_spreads
          lbl_metrics = 'spread'

        mix_rounds = list(range(0, len(l_metrics)))

        print('Preparing the chart...')

        chart_title = 'Whirlpool %s %s (pools %s)' % (lbl_direction, lbl_metrics, o_metrics.snapshot.denom)

        scatter = go.Scatter(
          x=mix_rounds,
          y=l_metrics,
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
              text='mix round',
              font=font_axes
            )
          ),
          yaxis=go.layout.YAxis(
            title=go.layout.yaxis.Title(
              text=lbl_metrics,
              font=font_axes
            )
          )
        )

        fig.show(config={
          'scrollZoom': True,
          'displayModeBar': True,
          'editable': True
        })

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
