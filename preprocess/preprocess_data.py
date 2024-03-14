import numpy as np
import pandas as pd
import os

input_path_prep = os.path.join(os.getcwd(), "..", "data")


# input_prep_path = os.path.join(os.getcwd(), "..", "data", "prepared")

def get_output_path(input_path):
    output_path = os.path.join(input_path, "prepared")  # where prepared files will be stored
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    return output_path


file_info = {
    "S1.csv": {"headers": ["timestamp", "sensorId", "pizzaId"], "has_change": False, "range": None},
    "S2.csv": {"headers": ["timestamp", "sensorId", "pizzaId"], "has_change": False, "range": None},
    "S3.csv": {"headers": ["timestamp", "sensorId", "pizzaId"], "has_change": False, "range": None},
    "S4.csv": {"headers": ["timestamp", "sensorId", "pizzaId"], "has_change": False, "range": None},
    "S5.csv": {"headers": ["timestamp", "sensorId", "pizzaId"], "has_change": False, "range": None},
    "S6.csv": {"headers": ["timestamp", "sensorId", "pizzaId"], "has_change": False, "range": None},
    "S7.csv": {"headers": ["timestamp", "sensorId", "packId"], "has_change": False, "range": None},
    "S8.csv": {"headers": ["timestamp", "sensorId", "packId"], "has_change": False, "range": None},
    # EV: Removed type, not used by v3
    "S9.csv": {"headers": ["timestamp", "sensorId", "boxId"], "has_change": False, "range": None},
    "S10.csv": {"headers": ["timestamp", "sensorId", "boxId"], "has_change": False, "range": None},
    "S11.csv": {"headers": ["timestamp", "sensorId", "palletId"], "has_change": False, "range": None},
    "S12.csv": {"headers": ["timestamp", "sensorId", "palletId"], "has_change": False, "range": None},
    "S13.csv": {"headers": ["timestamp", "sensorId", "palletId"], "has_change": False, "range": None},
    "S14.csv": {"headers": ["timestamp", "sensorId", "palletId"], "has_change": False, "range": None},
    "S15.csv": {"headers": ["timestamp", "sensorId", "palletId"], "has_change": False, "range": None},
    "S16.csv": {"headers": ["timestamp", "sensorId", "palletId"], "has_change": False, "range": None},
    "S100.csv": {
        "headers": ["timestamp", "sensorId", "pizzaId", "exceededCookingTime"], "has_change": False, "range": None
    },
    "S101.csv": {"headers": ["timestamp", "sensorId", "pizzaId"], "has_change": False, "range": None},
    "S102.csv": {"headers": ["timestamp", "sensorId", "packId"], "has_change": False, "range": None},
    "S103.csv": {"headers": ["timestamp", "sensorId", "boxId"], "has_change": False, "range": None},
    "S104.csv": {"headers": ["timestamp", "sensorId", "packId"], "has_change": False, "range": None},
    "S105.csv": {"headers": ["timestamp", "sensorId", "pizzaId"], "has_change": False, "range": None},
    "S106.csv": {"headers": ["timestamp", "sensorId", "boxId"], "has_change": False, "range": None},
    "In1_distanceLock.csv": {"headers": ["timestamp", "sensorId", "locked"], "has_change": True, "range": None},
    "In1_policyLock.csv": {"headers": ["timestamp", "sensorId", "locked"], "has_change": True, "range": None},
    "opBox_onBreak.csv": {"headers": ["timestamp", "operatorId", "hasBreak"], "has_change": False, "range": None},
    "opPack_onBreak.csv": {"headers": ["timestamp", "operatorId", "hasBreak"], "has_change": False, "range": None},
    "wip.csv": {"headers": ["timestamp", "sensorId", "amount"], "has_change": False, "range": None}
}


def prepare_sig_change_file(df, column_name, range_size=.5):
    df["diff"] = df[column_name].diff(1)
    sumvals = np.frompyfunc(lambda a, b: a + b if abs(a) <= range_size else b, 2, 1)

    df['cumvals'] = sumvals.accumulate(df['diff'], dtype=object)
    df["sig_change"] = abs(df['cumvals']) > range_size
    df.loc[df["cumvals"].isna(), "sig_change"] = True
    df = df.loc[df["sig_change"] == True, ["timestamp", "sensorId", column_name]]

    return df


def add_headers_to_csv(input_path, file_name, headers, has_change, _range, file_suffix):
    df = pd.read_csv(os.path.join(input_path, file_name), sep=";", names=headers)
    if has_change:
        sensor_value_name = headers[-1]
        df = model_changes(df, sensor_value_name)
        if _range is not None:
            range_size = df[sensor_value_name].std() * _range
            df = prepare_sig_change_file(df, sensor_value_name, range_size=range_size)

    output_path = get_output_path(input_path)
    file_name_without_extension = os.path.splitext(file_name)[0]
    df.to_csv(os.path.join(output_path, f"{file_name_without_extension}{file_suffix}.csv"), sep=";", index=False)


def model_changes(df, sensor_value_name="Power"):
    df["shift"] = df[sensor_value_name].shift(1)

    df["sig_change"] = df["shift"] != df[sensor_value_name]
    df = df.loc[df["sig_change"] == True, ["timestamp", "sensorId", sensor_value_name]]

    return df


def prepare_files(input_path, file_suffix=""):
    for file_name, file_info_dict in file_info.items():
        headers = file_info_dict["headers"]
        change_level = file_info_dict["has_change"]
        _range = file_info_dict["range"]
        add_headers_to_csv(input_path, file_name, headers, change_level, _range, file_suffix)


if __name__ == "__main__":
    prepare_files(input_path=input_path_prep)
