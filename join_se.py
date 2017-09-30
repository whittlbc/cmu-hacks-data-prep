from src.utils import join_csvs
from src.helpers.definitions import se_dir, data_dir

combo_file_path = data_dir + '/combo_se.csv'

join_csvs(se_dir, on='emcg_uuid', dest=combo_file_path)