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
from whirlpool_stats.services.downloader import Downloader
from whirlpool_stats.services.snapshot import Snapshot
from whirlpool_stats.services.forward_metrics import ForwardMetrics
from whirlpool_stats.services.backward_metrics import BackwardMetrics
from whirlpool_stats.services.tx0s_metrics import Tx0sMetrics
from whirlpool_stats.services.exporter import Exporter
from whirlpool_stats.services.metrics_plotter import Plotter
from whirlpool_stats.services.tx_scores import TxScores
from whirlpool_stats.services.pools_capacity import PoolsCapacity


class WhirlpoolStats(Cmd):

  def __init__(self, working_dir, socks5, rpc_connection_uri):
    '''
    Constructor
    '''
    super(WhirlpoolStats, self).__init__()
    self.working_dir = working_dir
    self.socks5 = socks5
    self.rpc_connection_uri = rpc_connection_uri
    
    # Snapshot loaded in memory
    self.snapshot = Snapshot(self.working_dir)
    # Forward looking metrics
    self.fwd_metrics = ForwardMetrics(self.snapshot)
    # Backward looking metrics
    self.bwd_metrics = BackwardMetrics(self.snapshot)
    # Tx0s metrics
    self.tx0_metrics = Tx0sMetrics(self.snapshot)
    # Exporter
    self.exporter = Exporter(
      self.fwd_metrics,
      self.bwd_metrics,
      self.tx0_metrics
    )
    # Metrics plotter
    self.plotter = Plotter(
      self.fwd_metrics,
      self.bwd_metrics,
      self.tx0_metrics
    )


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
Downloads the txids of all mixes and Tx0s of all pools
or downloads the snapshot(s) for one or several pool denominations
Available denomnination codes are 05, 005, 001, 0001
Examples:
  download txids      => downloads the txids of mixes and tx0s of all pools
  download 05         => downloads the snapshot of the 0.5BTC pools
  download 005,001    => downloads the snapshots of the 0.05BTC and 0.01BTC pools
  download            => downloads the snapshots of all denominations
    '''
    print('')
    downloader = Downloader()
    if len(args) == 0:
      downloader.download(self.working_dir, ALL_DENOMS, self.socks5)
    elif args == 'txids':
      downloader.download_txids(self.working_dir, self.socks5)
    else:
      denoms = args.split(',') 
      downloader.download(self.working_dir, denoms, self.socks5)
    print(' ')


  def do_load(self, args):
    '''
Loads in memory the snapshot of a given denomination
and computes its metrics
Available denomnination codes are 05, 005, 001, 0001
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
Syntax: score <txid> [denom]
Examples:
  score 450f236d596fc8a43916d624734fa7608cff1f17af5c3ddf81d7ad79021a645d
  score 450f236d596fc8a43916d624734fa7608cff1f17af5c3ddf81d7ad79021a645d 05
    '''
    print('')

    txid = None
    denom = None

    if len(args) == 0:
      print('The txid of a mix transaction is mandatory.')
      print(' ')
      return
    else:
      l_args = args.split(' ')
      txid = l_args[0]
      if len(l_args) == 2:
        denom = l_args[1]     
    
    snapshot = Snapshot(self.working_dir)
    scores_processor = TxScores(snapshot)
    scores = scores_processor.compute(txid, denom)

    print(' ')

    if scores is None:
      print('Unable to find this transaction in snapshots available in the working directory.')

    elif scores['type'] == 'mix': 
      print('Backward-looking metrics for the outputs of this mix:')
      print('  anonset = %d' % scores['bwd_anonset'])
      print('  spread = %d%%' % scores['bwd_spread'])
      print('')
      print('Forward-looking metrics for Tx0s outputs having this transaction as their first mix:')
      print('  anonset = %d' % scores['fwd_anonset'])
      print('  spread = %d%%' % scores['fwd_spread'])

    else:
      heterogeneity = float(scores['nb_counterparties']) / float(scores['nb_outs'])
      print('Metrics for this Tx0:')
      print('  number of mixed outputs = %d' % scores['nb_outs'])
      print('  number of counterparties (tx0s) = %d' % scores['nb_counterparties'])
      print('  heterogeneity ratio = %.2f' % heterogeneity)

    print(' ')


  def do_plot(self, args):
    '''
Plots a chart for a given metrics.

Syntax: plot <category> <name> [log]

Available charts:

- Forward-looking privacy metrics ----------------------------------------------------------------------------------------
    plot fwd anonset        => plot a scatterplot displaying the forward looking anonsets
    plot fwd spread         => plot a scatterplot displaying the forward looking spreads

- Backward-looking privacy metrics ---------------------------------------------------------------------------------------
    plot bwd spread         => plot a scatterplot displaying the backward looking spreads
    plot bwd spread         => plot a scatterplot with the y-axis in log scale

- Activity metrics -------------------------------------------------------------------------------------------------------
    plot act inflow         => plot a linechart of the daily inflow expressed in number of UTXOs entering the pool
    plot act mixes          => plot a linechart of the daily number of mixes
    plot act tx0s_created   => plot a linechart of the daily number of Tx0s created
    plot act tx0s_active    => plot a linechart of the daily number of active Tx0s

- Tx0s metrics -----------------------------------------------------------------------------------------------------------
    plot tx0 outputs        => plot a scatterplot displaying the number of outputs generated by the Tx0s
    plot tx0 hr             => plot a scatterplot displaying the heteogeneity ratio of the Tx0s
    plot tx0 hrout          => plot a scatterplot displaying the heteogeneity ratio vs the number of mixed Tx0s outputs
    plot tx0 hrdist         => plot a histogram displaying the distribution of Tx0s per heterogeneity ratio
    '''
    print('')

    if len(args) == 0:
      print('Category and metrics are mandatory.')
    else:
      l_args = args.split(' ')
      category = l_args[0]
      metrics = l_args[1]
      log_scale = True if ((len(l_args) == 3) and l_args[2] == 'log') else False
      self.plotter.plot(category, metrics, log_scale)
      
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
    self.exporter.export(export_dir)
    print(' ')


  def do_capacity(self, args):
    '''
Computes the unspent capacity of all pools.
Examples:
  capacity          => computes the premix and postmix capacities of all pools
  capacity postmix  => computes the postmix capacities of all pools
  capacity premix   => computes the premix capacities of all pools
    '''
    print('')

    if len(args) == 0:
      mode = 'all'
    elif args == 'premix':
      mode = 'premix'
    elif args == 'postmix':
      mode = 'postmix'
    else:
      mode = 'all'

    capacity_processor = PoolsCapacity(self.working_dir, self.socks5, self.rpc_connection_uri)
    
    if mode == 'postmix':
      capacities = capacity_processor.compute_postmix_capacities()
    elif mode == 'premix':
      capacities = capacity_processor.compute_premix_capacities()
    else:
      capacities = capacity_processor.compute_capacities()
    
    print(' ')
    print(' ')
    print('---------------------------------')
    print('Results                          ')
    print('---------------------------------')
    nb_utxos = 0
    amount = 0
    
    for denom in ALL_DENOMS:
      if denom in capacities:
        capacity = capacities[denom]
        btc_amount = capacity['amount'] / 100000000.0
        print(' ')
        print('Pool %s:' % denom)
        print('  Number of UTXOs = %d' % capacity['utxos'])
        print('  Cumulated amount of UTXOs = %.8f BTC' % btc_amount)
        nb_utxos += capacity['utxos'] 
        amount += capacity['amount'] 
   
    print(' ')
    btc_amount = amount / 100000000.0
    print('Total:')
    print('  Number of UTXOs = %d' % nb_utxos)
    print('  Cumulated amount of UTXOs = %.8f BTC' % btc_amount)

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
  sys.stdout.write('python wst.py [--workdir=/tmp] [--socks5=localhost:9050] [--rpc=http://username:password@host:port]\n')
  sys.stdout.write('\n\n[-w OR --target_dir] = Path of the directory that will store the snapshot files.')
  sys.stdout.write('\n\n[-s OR --socks5] = Url of the socks5 proxy to use for downloading the snapshot.')
  sys.stdout.write('\n\n[-r OR --rpc] = Connection url to bitcoind RPC API. Format = http://username:password@host:port')
  sys.stdout.flush()


if __name__ == '__main__':
  # Initializes the parameters
  working_dir = '/tmp'
  socks5 = None
  rpc_connection_uri = ''
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
    elif opt in ('-r', '--rpc'):
      rpc_connection_uri = arg

  wst = WhirlpoolStats(working_dir, socks5, rpc_connection_uri)
  wst.set_prompt()
  wst.cmdloop('Starting Whirlpool Stats Tools...\nType "help" for a list of available commands.\n')
