import pandas as pd
from pathlib import Path

lastIteration = 150
modified = False
desiredMaxSpeed = 100

it = lastIteration
base_path = Path("../matsim-kelheim/output")


file_path_modified = base_path / f"modified-s{desiredMaxSpeed}.0-i{lastIteration}" / "ITERS" / f"it.{it}" / f"kelheim-id.{it}.trips.csv.gz"
file_path_unmodified = base_path / f"unmodified-i{lastIteration}" / "ITERS" / f"it.{it}" / f"kelheim-id.{it}.trips.csv.gz"


def load_trips_data(file_path):
    df_output = pd.read_csv(file_path, sep=';')

    # Convert time strings to hours
    df_output['trav_time'] = pd.to_timedelta(df_output['trav_time']).dt.total_seconds() / 3600
    df_output['wait_time'] = pd.to_timedelta(df_output['wait_time']).dt.total_seconds() / 3600

    # Convert distances to kilometers
    df_output['traveled_distance'] = pd.to_numeric(df_output['traveled_distance'], errors='coerce') / 1000

    return df_output


def aggregate_data_by(dataframe, aggregation_method="sum", by="main_mode"):
    agg_columns = ['trav_time', 'traveled_distance']
    agg_dataframe = dataframe.groupby(by)[agg_columns].agg(aggregation_method).reset_index()
    agg_dataframe.columns = [by, f'{aggregation_method}_trav_time', f'{aggregation_method}_distance']

    if aggregation_method == "sum":
        trip_counts = dataframe.groupby(by).size().reset_index(name='trip_count')
        agg_dataframe = pd.merge(agg_dataframe, trip_counts, on=by, how='left')
    else:
        agg_dataframe['trip_count'] = None

    return agg_dataframe


df = load_trips_data(file_path_modified if modified else file_path_unmodified)

sum_df = aggregate_data_by(df, "sum", "main_mode")
mean_df = aggregate_data_by(df, "mean", "main_mode")

# Create result table
modes = sorted(df['main_mode'].unique())

result = pd.DataFrame(index=[
    "Number of trips",
    "Total time traveled [h]",
    "Total distance traveled [km]",
    "Average speed [km/h]",
    "Avg. time traveled per trip [h]",
    "Avg. distance traveled per trip [km]"
], columns=modes)

for mode in modes:
    # Extract rows from both sum and mean dfs
    row_sum = sum_df[sum_df['main_mode'] == mode].iloc[0]
    row_mean = mean_df[mean_df['main_mode'] == mode].iloc[0]

    # Fill in values
    result.at["Number of trips", mode] = int(row_sum['trip_count'])
    result.at["Total time traveled [h]", mode] = row_sum['sum_trav_time']
    result.at["Total distance traveled [km]", mode] = row_sum['sum_distance']
    result.at["Average speed [km/h]", mode] = row_sum['sum_distance'] / row_sum['sum_trav_time']
    result.at["Avg. time traveled per trip [h]", mode] = row_mean['mean_trav_time']
    result.at["Avg. distance traveled per trip [km]", mode] = row_mean['mean_distance']

result.to_csv(f"output/{modified}_mode_comparison_stacked_{it}.csv")