'''
Copyright (c) 2019 Katana Cryptographic Ltd. All Rights Reserved.

A class allowing to compute the unspent capacity of all pools
'''
import os
import sys
import csv
import decimal
from collections import defaultdict
from whirlpool_stats.utils.constants import *
from whirlpool_stats.services.downloader import Downloader
from whirlpool_stats.utils.bitcoind_wrapper import BitcoindWrapper


class PoolsCapacity(object):

  def __init__(self, working_dir, socks5, rpc_connection_uri):
    '''
    Constructor
    Parameters:
      working_dir        = path of the directory that stores txids files
      socks5             = url of the socks5 proxy to use (or None)
      rpc_connection_uri = connection uri to the bitcoind RPC API
    '''
    self.working_dir = working_dir
    self.socks5 = socks5
    self.rpc_connection_uri = rpc_connection_uri


  def compute_premix_capacities(self):
    '''
    Computes the premix unspent capacities of all pools
    '''
    # Checks if txids files are found in the working directory
    test_filename = '%s_%s.csv' % (FN_MIX_TXIDS, DENOM_05)
    test_filepath = '%s/%s' % (self.working_dir, test_filename)
    if not os.path.exists(test_filepath):
      # Txids files not found. Downloads them.
      downloader = Downloader()
      downloader.download_txids(self.working_dir, self.socks5)
    
    # Initializes Bitcoind RPC wrapper
    self.btc_wrapper = BitcoindWrapper()
    self.btc_wrapper.connect(self.rpc_connection_uri)
    
    result = dict()

    # Iterates over the pools
    for denom in ALL_DENOMS:
      premix_nb_utxos = 0
      premix_amount = 0
  
      # Processes premix wallets
      print('Started processing Tx0s from pool %s' % denom)

      filename = '%s_%s.csv' % (FN_TX0S_TXIDS, denom)
      filepath = '%s/%s' % (self.working_dir, filename)

      with open(filepath, newline='\n') as csvfile:
        file_reader = csv.reader(csvfile, delimiter=';')
        next(file_reader, None)  # skips the headers
        nb_tx0s = 0
        txids = []
        # Iterates over all tx0s
        for row in file_reader:
          txids.append(row[0])
          nb_tx0s += 1
          # Processed a batch of 100 tx0s
          if nb_tx0s % 100 == 0:
            try:
              nb_utxos, amount = self.get_tx0s_capacity(txids)
              premix_nb_utxos += nb_utxos
              premix_amount += amount
              print('  Processed %d Tx0s' % nb_tx0s)
              txids = []
            except Exception as e:
              print('A problem was met while computing the unspent capacity\n', e)
              return result
        # Processes last batch of tx0s
        try:
          nb_utxos, amount = self.get_tx0s_capacity(txids)
          premix_nb_utxos += nb_utxos
          premix_amount += amount
          print('  Processed %d Tx0s' % nb_tx0s)
        except Exception as e:
          print('A problem was met while computing the unspent capacity\n', e)
          return result

      print('Completed processing of Tx0s from pool %s' % denom)

      result[denom] = {
        'utxos': premix_nb_utxos,
        'amount': premix_amount
      }

    return result


  def compute_postmix_capacities(self):
    '''
    Computes the postmix unspent capacities of all pools
    '''
    # Checks if txids files are found in the working directory
    test_filename = '%s_%s.csv' % (FN_MIX_TXIDS, DENOM_05)
    test_filepath = '%s/%s' % (self.working_dir, test_filename)
    if not os.path.exists(test_filepath):
      # Txids files not found. Downloads them.
      downloader = Downloader()
      downloader.download_txids(self.working_dir, self.socks5)
    
    # Initializes Bitcoind RPC wrapper
    self.btc_wrapper = BitcoindWrapper()
    self.btc_wrapper.connect(self.rpc_connection_uri)
    
    result = dict()

    # Iterates over the pools
    for denom in ALL_DENOMS:
      postmix_nb_utxos = 0
      postmix_amount = 0
        
      # Processes postmix wallets
      print('Started processing mixes from pool %s' % denom)

      filename = '%s_%s.csv' % (FN_MIX_TXIDS, denom)
      filepath = '%s/%s' % (self.working_dir, filename)

      with open(filepath, newline='\n') as csvfile:
        file_reader = csv.reader(csvfile, delimiter=';')
        next(file_reader, None)  # skips the headers
        mix_round = 0
        txids = []
        nb_txos = []
        # Iterates over all mixes
        for row in file_reader:
          txids.append(row[0])
          nb_txos.append(int(row[1]))
          mix_round += 1
          # Processed a batch of 100 mixes
          if mix_round % 100 == 0:
            try:
              nb_utxos, amount = self.get_mixes_capacity(txids, nb_txos)
              postmix_nb_utxos += nb_utxos
              postmix_amount += amount
              print('  Processed %d mixes' % mix_round)
              txids = []
              nb_txos = []
            except Exception as e:
              print('A problem was met while computing the unspent capacity\n', e)
              return result
        # Processes last batch of mixes
        try:
          nb_utxos, amount = self.get_mixes_capacity(txids, nb_txos)
          postmix_nb_utxos += nb_utxos
          postmix_amount += amount
          print('  Processed %d mixes' % mix_round)
        except Exception as e:
          print('A problem was met while computing the unspent capacity\n', e)
          return result

      print('Completed processing of mixes from pool %s' % denom)

      result[denom] = {
        'utxos': postmix_nb_utxos,
        'amount': postmix_amount
      }

    return result


  def compute_capacities(self):
    '''
    Computes the premix+postmix unspent capacities of all pools
    '''
    capacities = dict()
    postmix_capacities = self.compute_postmix_capacities()
    premix_capacities = self.compute_premix_capacities()
    for denom in ALL_DENOMS:
      res = {'utxos': 0, 'amount': 0}
      if denom in premix_capacities: 
        res['utxos'] += premix_capacities[denom]['utxos']
        res['amount'] += premix_capacities[denom]['amount']
      if denom in postmix_capacities: 
        res['utxos'] += postmix_capacities[denom]['utxos']
        res['amount'] += postmix_capacities[denom]['amount']
      capacities[denom] = res
    return capacities



  def get_mixes_capacity(self, txids, nbs_txos):
    nb_utxos = 0
    amount = 0
    outpoints = []
    for i in range(0, len(txids)):
      txid = txids[i]
      nb_txos = nbs_txos[i]
      for i in range(0, nb_txos):
        outpoints.append((txid, i))
    utxos = self.btc_wrapper.get_txouts(outpoints, False)
    for utxo in utxos:
      if utxo is not None:
        nb_utxos += 1
        amount += int(round(decimal.Decimal(utxo['value']) * decimal.Decimal(1e8)))
    return nb_utxos, amount


  def get_tx0s_capacity(self, txids):
    nb_utxos = 0
    amount = 0
    outpoints = []
    txs = self.btc_wrapper.get_transactions(txids)
    for tx in txs:
      if tx is not None:
        denom = self.get_tx0_denom(tx)
        for vout in tx['vout']:
          amount = int(round(decimal.Decimal(vout['value']) * decimal.Decimal(1e8)))
          if amount == denom:
            outpoints.append((tx['txid'], vout['n']))
    utxos = self.btc_wrapper.get_txouts(outpoints, False)
    for utxo in utxos:
      if utxo is not None:
        nb_utxos += 1
        amount += int(round(decimal.Decimal(utxo['value']) * decimal.Decimal(1e8)))
    return nb_utxos, amount


  def get_tx0_denom(self, tx):
    nb_outs_per_denom = defaultdict(int)
    for vout in tx['vout']:
      amount = int(round(decimal.Decimal(vout['value']) * decimal.Decimal(1e8)))
      nb_outs_per_denom[amount] += 1

    max_nb_items = 0
    denom = 0
    for k,v in nb_outs_per_denom.items():
      if v > max_nb_items:
        max_nb_items = v
        denom = k
      elif (v == max_nb_items) and (k > denom):
        denom = k

    return denom
