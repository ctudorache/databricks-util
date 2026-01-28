import os
import sys
import json
import shutil
import datetime

from typing import List

sys.path.insert(0, '..') # directory containing "my_util/"
from my_util.csv_util import zip_dir_for_download

def export_tollguru_request(output_dir: str, created_dt: datetime.datetime, polyline: str, timestamps: List[int], is_before_trip: bool, order_id: int):
    get_tolls_dt_str = created_dt.strftime('%Y-%m-%d-%H-%M-%S')
        
    req = {
        "mapProvider": "osrm",
        "polyline": polyline,
        "locTimes": [[n, ts] for n, ts in enumerate(timestamps)],
        "vehicle": {"type": "2AxlesAuto"},
        "includeParkingFee": True
    }

    req_json = json.dumps(req, indent=4)
    before_or_after_trip_str = "before-trip" if is_before_trip else "after-trip"
    output_filename = f'order-{order_id}-ts-{get_tolls_dt_str}-{before_or_after_trip_str}.json'
    output_filepath = os.path.join(output_dir, output_filename)

    with open(output_filepath, 'w') as f:
        f.write(req_json)

    return output_filepath

def export_tollguru_requests_to_json_for_download(df, df_name: str):
    output_dirpath = f'/dbfs/ctudorache/tmp/{df_name}/{df_name}-tollguru-requests'
    if os.path.exists(output_dirpath):
        print(f"Removing existing output dir: {output_dirpath}")
        shutil.rmtree(output_dirpath)
    os.makedirs(output_dirpath, exist_ok=True)
    print(f"Created output dir: {output_dirpath}")

    print(f"Exporting #{len(df)} requests to: {output_dirpath}")
    for index, row in df.iterrows():
        export_tollguru_request(
            output_dir=output_dirpath,
            created_dt = row['created'],
            polyline = row['polyline'],
            timestamps = list(map(int, json.loads(row['timestamps']))),
            is_before_trip = not row['is_price_prediction'],
            order_id = row['order_id']
        )

    zip_dir_for_download(output_dirpath)