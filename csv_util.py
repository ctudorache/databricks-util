import tempfile
import zipfile
import os
import shutil
import csv
from IPython.display import Markdown

def str_human_size(num, suffix="B"):
    for unit in ("", "K", "M", "G", "T", "P", "E", "Z"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

def str_human_filesize(filepath):
    return str_human_size(os.path.getsize(filepath))

def mk_file_download_url(filepath):
    file_storage_relative_path = filepath.replace('/dbfs/FileStore/', '')
    return f'https://bolt-geo.cloud.databricks.com/files/{file_storage_relative_path}'

def mk_print(text):
    display(Markdown(text + "<br>"))

def mk_link(text, url):
    return f"[{text}]({url})"

def file_download_link(filepath):
    return mk_link(filepath, mk_file_download_url(filepath))

def delete_dir(dirpath):
    if os.path.exists(dirpath):
        print(f"Deleting: {dirpath}")
        shutil.rmtree(dirpath)

def list_dir_files(root_dir):
    subfiles = []
    for dir_, _, files in os.walk(root_dir):
        for file_name in files:
              rel_dir = os.path.relpath(dir_, root_dir)
              rel_file = os.path.join(rel_dir, file_name)
              subfiles.append(rel_file)
    # with os.scandir(dirpath) as entries:
    #     for entry in entries:
    #         if entry.is_file():
    #             subfiles.append(entry.path)
    #         elif entry.is_dir():
    #             ### TODO(CTudorache): fix to append dirpath to subfiles
    #             subfiles.extend(list_dir_files(os.path.join(dirpath, entry.path)))
    return subfiles

def zip_files_for_download(root_dir, filepaths, zip_filename = None):
    if not filepaths:
        raise Exception("No input files")
    
    if zip_filename is None:
        zip_filename = os.path.basename(filepaths[0])

    download_zip_filepath = f"/dbfs/FileStore/ctudorache/{os.path.basename(zip_filename)}.zip"

    print(f"Zipping: root: {root_dir}, files: #{len(filepaths)} : {filepaths[0]} ... => {download_zip_filepath}")

    # cannot write directly to /dbfs . First write to a local disk (line /tmp), then move the file to desired location
    tmp_zip_file = tempfile.NamedTemporaryFile(delete=False)
    tmp_zip_filepath = tmp_zip_file.name
    print(f"Using temp file: {tmp_zip_filepath}")

    with zipfile.ZipFile(tmp_zip_filepath, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for filepath in filepaths:
            archive.write(os.path.join(root_dir, filepath), filepath)

    os.makedirs(os.path.dirname(download_zip_filepath), exist_ok=True)
    shutil.move(tmp_zip_filepath, download_zip_filepath)

    print(f"Done. ZIP: {download_zip_filepath} => {str_human_filesize(download_zip_filepath)}")
    mk_print("Download: " + file_download_link(download_zip_filepath))
        
def zip_dir_for_download(dirpath):
    filepaths = list_dir_files(dirpath)
    zip_filename = os.path.basename(dirpath)
    return zip_files_for_download(dirpath, filepaths, zip_filename)

def save_panda_df_to_csv_for_download(df, df_name, chunk_size):
    csv_filepath = f'/dbfs/ctudorache/tmp/{df_name}/{df_name}-data.csv'

    parent_dirpath = os.path.dirname(csv_filepath)
    os.makedirs(parent_dirpath, exist_ok=True)

    csv_filename = os.path.basename(csv_filepath)
    if csv_filename.endswith('.csv'):
        csv_filename = csv_filename[:-4]

    row_count = len(df.index)
    chunk_count = row_count // chunk_size + 1

    print(f"Saving: {csv_filepath}, rows: {row_count}, chunk_size: {chunk_size} => chunk_count: {chunk_count}")

    # save CSV files
    csv_filenames = []
    for i in range(0, row_count, chunk_size):
        chunk_index = i // chunk_size
        chunk_suffix = '' if chunk_index == 0 else f'_{chunk_index}'
        chunk_filename = f'{csv_filename}{chunk_suffix}.csv'
        output_chunk_filepath = os.path.join(parent_dirpath, chunk_filename)
        print(f" - Writing chunk: {output_chunk_filepath}")
        df.iloc[i:i+chunk_size].to_csv(output_chunk_filepath, mode='w', index=False, quoting=csv.QUOTE_NONNUMERIC)
        csv_filenames.append(chunk_filename)

    # zip CSV files
    zip_files_for_download(parent_dirpath, csv_filenames)


# delete_dir('/dbfs/ctudorache/tmp')
