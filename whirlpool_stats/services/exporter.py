'''
Copyright (c) 2019 Katana Cryptographic Ltd. All Rights Reserved.

A class exporting the computed metrics in CSV format
'''

class Exporter(object):

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


  def export(self, export_dir):
    '''
    Exports the computed metrics for the active snapshot (csv format)
    Files are exported in a given directory or in the working directory if none provided
    Examples:
      export /tmp  => exports the results in the /tmp directory
      export       => exports the results in the working directory
    '''
    self.export_fwd_metrics(export_dir)
    self.export_bwd_metrics(export_dir)
    self.export_activity_metrics(export_dir)
    

  def export_fwd_metrics(self, export_dir):
    '''
    Exports the forward-looking metrics
    Parameters:
      export_dir = export directory
    '''
    filename = 'whirlpool_%s_forward_metrics.csv' % self.fwd_metrics.snapshot.denom
    filepath = '%s/%s' % (export_dir, filename)

    f = open(filepath, 'w')
    line = 'mix_round;anonset;spread\n'
    f.write(line)

    for r in range(0, len(self.fwd_metrics.l_anonsets)):
      line = '%d;%d;%.2f\n' % (
        r,
        self.fwd_metrics.l_anonsets[r],
        self.fwd_metrics.l_spreads[r]
      )
      f.write(line)

    f.close()
    print('Exported forward-looking metrics in %s' % filepath)


  def export_bwd_metrics(self, export_dir):
    '''
    Exports the backward-looking metrics
    Parameters:
      export_dir = export directory
    '''
    # Exports backward-looking metrics
    filename = 'whirlpool_%s_backward_metrics.csv' % self.bwd_metrics.snapshot.denom
    filepath = '%s/%s' % (export_dir, filename)

    f = open(filepath, 'w')
    line = 'mix_round;anonset;spread\n'
    f.write(line)

    for r in range(0, len(self.bwd_metrics.l_anonsets)):
      line = '%d;%d;%.2f\n' % (
        r,
        self.bwd_metrics.l_anonsets[r],
        self.bwd_metrics.l_spreads[r]
      )
      f.write(line)

    f.close()
    print('Exported backward-looking metrics in %s' % filepath)


  def export_activity_metrics(self, export_dir):
    '''
    Exports the Tx0s metrics
    Parameters:
      export_dir = export directory
    '''
    # Exports activty metrics
    filename = 'whirlpool_%s_activity_metrics.csv' % self.bwd_metrics.snapshot.denom
    filepath = '%s/%s' % (export_dir, filename)

    f = open(filepath, 'w')
    line = 'date;nb_mixes;inflow;nb_new_tx0s;nb_active_tx0s\n'
    f.write(line)

    for k,v in self.bwd_metrics.d_nb_mixes.items():
      day = k.strftime('%d/%m/%Y')
      line = '%s;%d;%d;%d;%d\n' % (
        day,
        v, 
        self.bwd_metrics.d_inflow[k],
        self.tx0_metrics.d_nb_new_tx0s[k],
        self.bwd_metrics.d_nb_active_tx0s[k]
      )
      f.write(line)

    f.close()
    print('Exported activity metrics in %s' % filepath)
