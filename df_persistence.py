""" Saving Dataframe to disk. """

import os
import shutil
import hashlib
import pandas as pd;

# TODO(CTudorache): organise code into module (no need for Class, since all functions are static)

# TODO(CTudorache): auto cleanup old files

DF_PERSISTENCE_DIR = '/dbfs/ctudorache/df_persistence'

def str_human_size(num, suffix="B"):
    for unit in ("", "K", "M", "G", "T", "P", "E", "Z"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

def str_human_filesize(filepath):
    return str_human_size(os.path.getsize(filepath))

def delete_dir(dirpath):
    if os.path.exists(dirpath):
        print(f"Deleting: {dirpath}")
        shutil.rmtree(dirpath)

def df_persistence_log(msg):
    print("DFPersistence: " + msg)

def df_persistence_hash(sql_text):
    sql_hash = hashlib.md5(sql_text.encode()).hexdigest()
    return f'{sql_hash}'

def df_persistence_rootpath(df_name):
    return os.path.join(DF_PERSISTENCE_DIR, df_name)

def df_persistence_dirpath(df_name, sql_text):
    df_subdir = df_persistence_hash(sql_text)
    return os.path.join(df_persistence_rootpath(df_name), df_subdir)

def df_persistence_part_filename(chunk_index):
    return f'part-{chunk_index}.pkl'

def df_persistence_part_num(part_filename):
    return int(part_filename[5:-4])

def df_persistence_save(df_name, sql_text, df):
    delete_dir(df_persistence_rootpath(df_name)) # cleanup 

    df_dirpath = df_persistence_dirpath(df_name, sql_text)
    os.makedirs(df_dirpath, exist_ok=True)

    row_count = len(df.index)
    print(f"Saving: {df_dirpath}, rows: {row_count}")

    chunk_size = 500000
    for i in range(0, row_count, chunk_size):
        chunk_index = i // chunk_size
        part_filename = df_persistence_part_filename(chunk_index)
        part_filepath = os.path.join(df_dirpath, part_filename)
        df.iloc[i:i+chunk_size].to_pickle(part_filepath)
        df_persistence_log(f" - {part_filename}, size: {str_human_filesize(part_filepath)}")


def list_dir_files(dir_path, suffix):
    filenames = [f for f in os.listdir(dir_path) if f.endswith(suffix)]
    filenames.sort(key = lambda part_filename: df_persistence_part_num(part_filename))
    return filenames

def df_persistence_load(df_name, sql_text):
    df_dirpath = df_persistence_dirpath(df_name, sql_text)
    if not os.path.exists(df_dirpath):
        df_persistence_log(f"Not found: {df_dirpath}")
        return None
    
    filenames = list_dir_files(df_dirpath, '.pkl')
    df_persistence_log(f"Loading: {df_dirpath}")
    for f in filenames:
        df_persistence_log(f" - {f}, size: {str_human_filesize(os.path.join(df_dirpath, f))}")

    if (not filenames):
        df_persistence_log(f"Directory empty: {df_dirpath}")
        return None
    
    return  pd.concat([pd.read_pickle(os.path.join(df_dirpath, f)) for f in filenames])
    
def df_persistence_clear(df_name):
    dirpath = df_persistence_rootpath(df_name)
    if os.path.exists(dirpath):
        shutil.rmtree(dirpath)
    df_persistence_log(f"Cleanup: {dirpath}")

