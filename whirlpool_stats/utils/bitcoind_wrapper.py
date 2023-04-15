'''
Copyright (c) 2019 Katana Cryptographic Ltd. All Rights Reserved.

A class allowing to interact with the RPC API of a local full node.
'''
from decimal import *
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException


class BitcoindWrapperError(Exception):
  pass


class MissingBitcoindConfigError(BitcoindWrapperError):
  def __init__(self): 
    pass

  def __str__(self): 
    return 'Missing configuration for connection to bitcoind'


class MissingBitcoindConnectionError(BitcoindWrapperError):
  def __init__(self): 
    pass

  def __str__(self): 
    return 'Missing connection to bitcoind'


class BitcoindConnectionError(BitcoindWrapperError):
  def __init__(self): 
    pass

  def __str__(self): 
    return 'Connection to bitcoind has failed'


class BitcoindRequestError(BitcoindWrapperError):
  code = None
  message = ''

  def __init__(self, error): 
    self.code = error['code']
    self.message = error['message']

  def __str__(self): 
    return self.message


class BitcoindMiscError(BitcoindWrapperError):
  def __init__(self): 
    pass

  def __str__(self): 
    return 'An error has occured during communication with bitcoind'



class BitcoindWrapper(object):
  '''
  BitcoindWrapper allows to request bitcoind with RPC api calls
  '''

  # Default timeout for the rcp api. 
  RPC_API_DEFAULT_TIMEOUT = 30


  def __init__(self):
    '''
    Constructor
    '''
    pass


  def _check_connection_config(self):
    '''
    Checks if connection configuration is set
    Raises a MissingBitcoindConfigError if configuration is not set
    '''
    if self._rpc_uri is None:
      raise MissingBitcoindConfigError()


  def _check_connection_object(self):
    '''
    Checks if connection object is set
    Raises a MissingBitcoindConnectionError if configuration is not set
    '''
    if self._connection is None: 
      raise MissingBitcoindConnectionError()


  def connect(self, uri='', timeout=RPC_API_DEFAULT_TIMEOUT):
    '''
    Opens a connection to bitcoind        
    Parameters:
      uri     = connection uri
      timeout = timeout used for the rpc api (in seconds)
    '''        
    if uri:
      self._rpc_uri = uri

    self._check_connection_config()        

    try:
      self._connection = AuthServiceProxy(self._rpc_uri, timeout=timeout)
    except:
      raise BitcoindConnectionError()


  def check_connection(self):
    '''
    Checks connection with bitcoind
    '''        
    self._check_connection_config()
    self._check_connection_object()

    try:
      info = self._connection.getinfo()
      if info is None:
        raise BitcoindConnectionError()
      else:
        return True
    except JSONRPCException as e:
      raise BitcoindRequestError(e.error)
    except:
      raise BitcoindMiscError()



  def get_transactions(self, txids, verbose=True, retry=True):
    '''
    Gets the transactions corresponding to a given list of txids
    Parameters:
      txids     = ids of the transaction
      verbose   = boolean flag indicating if verbose result must be returned or just raw hex
      retry     = boolean flag indicating if request should be retried 
                  on a new connection if a problem is met
    '''
    if (txids is None) or (len(txids) == 0): 
      raise ParameterError('txids')

    self._check_connection_object()  

    try:
      commands = [['getrawtransaction', txid, int(verbose)] for txid in txids]
      return self._connection.batch_(commands)
    except JSONRPCException as e:
      raise BitcoindRequestError(e.error)
    except:
      if retry:
        self.connect(self._rpc_uri)
        return self.get_transactions(txids, verbose, False)
      else:
        raise BitcoindMiscError()


  def get_txouts(self, outpoints, include_mempool=True, retry=True):
    '''
    Gets the utxos corresponding to a given list of outpoints
    Parameters:
      outpoints       = list of tuples (id of the transaction, index of the output)
      include_mempool = boolean flag indicating if utxos from the mempool should be included
      retry           = boolean flag indicating if request should be retried 
                        on a new connection if a problem is met
    '''
    if (outpoints is None) or (len(outpoints) == 0): 
      raise ParameterError('outpoints')

    self._check_connection_object()  

    try:
      commands = [['gettxout', outpoint[0], outpoint[1], include_mempool] for outpoint in outpoints]
      return self._connection.batch_(commands)
    except JSONRPCException as e:
      raise BitcoindRequestError(e.error)
    except:
      if retry:
        self.connect(self._rpc_uri)
        return self._connection.get_txouts(outpoints, include_mempool, False)
      else:
        raise BitcoindMiscError()
