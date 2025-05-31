import pandas as pd
from pathlib import Path

lastIteration = 150
modified = True
desiredMaxSpeed = 100

it = lastIteration
base_path = Path("../matsim-kelheim/output")


file_path_modified = base_path / f"modified-s{desiredMaxSpeed}.0-i{lastIteration}" / "ITERS" / f"it.{it}" / f"kelheim-id.{it}.trips.csv.gz"
file_path_unmodified = base_path / f"unmodified-i{lastIteration}" / "ITERS" / f"it.{it}" / f"kelheim-id.{it}.trips.csv.gz"

affectedPeronsPath = base_path / "affectedPersons-s100.0.txt"

with open(affectedPeronsPath, 'r') as f:
    affectedPersons = set(line.strip() for line in f)

def load_trips_data(file_path):
    df_output = pd.read_csv(file_path, sep=';')

    # Convert time strings to hours
    df_output['trav_time'] = pd.to_timedelta(df_output['trav_time']).dt.total_seconds() / 3600
    df_output['wait_time'] = pd.to_timedelta(df_output['wait_time']).dt.total_seconds() / 3600

    # Convert distances to kilometers
    df_output['traveled_distance'] = pd.to_numeric(df_output['traveled_distance'], errors='coerce') / 1000
    df_output['euclidean_distance'] = pd.to_numeric(df_output['euclidean_distance'], errors='coerce') / 1000

    df_output_affected = df_output[df_output['person'].isin(affectedPersons)]
    return df_output, df_output_affected


def aggregate_data_by(dataframe, aggregation_method="sum", by="main_mode"):
    agg_columns = ['trav_time', 'traveled_distance', 'euclidean_distance']
    agg_dataframe = dataframe.groupby(by)[agg_columns].agg(aggregation_method).reset_index()
    agg_dataframe.columns = [by, f'{aggregation_method}_trav_time', f'{aggregation_method}_distance',
                             f'{aggregation_method}_euclidean_distance']

    if aggregation_method == "sum":
        trip_counts = dataframe.groupby(by).size().reset_index(name='trip_count')
        agg_dataframe = pd.merge(agg_dataframe, trip_counts, on=by, how='left')
    else:
        agg_dataframe['trip_count'] = None

    return agg_dataframe


def aggregate_data_and_save(dataframe, is_modified):
    sum_df = aggregate_data_by(dataframe, "sum", "main_mode")
    mean_df = aggregate_data_by(dataframe, "mean", "main_mode")

    # Create result table
    modes = sorted(dataframe['main_mode'].unique())

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

    result.to_csv(f"output/aP/{is_modified}_mode_comparison_stacked_{it}.csv")


df_modified, filtered_df_modified = load_trips_data(file_path_modified)
df_unmodified, filtered_df_unmodified = load_trips_data(file_path_unmodified)
number_of_persons = len(sorted(df_unmodified['person'].unique()))
print(f"Number of persons: {number_of_persons}, number of affected persons: {len(affectedPersons)}")
print(f"Number of persons in filtered modified: {len(filtered_df_modified['person'].unique())}, "
      f"Number of persons in filtered unmodified: {len(filtered_df_unmodified['person'].unique())}")

sum_filtered_df_modified = aggregate_data_by(filtered_df_modified, "sum", "person")
sum_filtered_df_unmodified = aggregate_data_by(filtered_df_unmodified, "sum", "person")

merged = sum_filtered_df_unmodified.merge(sum_filtered_df_modified, on='person', suffixes=('_unmod', '_mod'))
merged['euclidean_distance_diff'] = merged['sum_euclidean_distance_mod'] - merged['sum_euclidean_distance_unmod']
merged['distance_diff'] = merged['sum_distance_mod'] - merged['sum_distance_unmod']
merged['trav_time_diff'] = merged['sum_trav_time_mod'] - merged['sum_trav_time_unmod']


changed_agents = merged[merged['euclidean_distance_diff'].abs() > 0]
print(f"Number of agents with changed trips: {len(changed_agents)}")

merged.to_csv('output/aP/merged.csv', index=False)


#aggregate_data_and_save(filtered_df_modified, True)
