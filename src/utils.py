import pandas
import glob


def join_csvs(dir=None, sep=',', on=None, dest=None):
  print 'Joining CSVs in directory: {}'.format(dir)

  csvs = glob.glob('{}/*.csv'.format(dir.rstrip('/')))

  print 'Reading {}...'.format(csvs[0])
  combo_csv = pandas.read_csv(csvs[0], sep=sep)

  for csv_path in csvs[1:]:
    import code; code.interact(local=locals())
    print 'Reading {}...'.format(csv_path)
    csv = pandas.read_csv(csv_path, sep=sep)
    print 'Joining...'.format(csv_path)
    combo_csv = combo_csv.merge(csv, on=on)

  print 'Saving combo CSV to {}...'.format(dest)
  combo_csv.to_csv(dest, sep=sep)