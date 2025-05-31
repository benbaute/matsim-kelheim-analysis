import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the CSV
df = pd.read_csv('output/aP/merged.csv')  # Adjust the filename as needed

df['trav_time_pct_change'] = (df['trav_time_diff'] / df['sum_trav_time_unmod']) * 100
df['distance_pct_change'] = (df['distance_diff'] / df['sum_distance_unmod']) * 100

outlier_threshold = 100  # in %
outliers = df[df['trav_time_pct_change'].abs() > outlier_threshold]
print(f"Number of outliers: {len(outliers)}. If significant, analyze further!")
print(f"Outliers (more than {outlier_threshold}% change): {outliers['person'].values}")

no_relevant_threshold = 1  # in %
no_relevant_change = df[df['trav_time_pct_change'].abs() < no_relevant_threshold]
print(f"{len(no_relevant_change)}/{len(df)} have travel time change below {no_relevant_threshold}%.")
print(f"{len(df) - len(no_relevant_change)} are affected by modification and have travel time change more than "
      f"{no_relevant_threshold}%.")

# Filter outliers for better visualization. If there are many outliers, the following graphs are not accurate!
df = df[df['trav_time_pct_change'].abs() <= outlier_threshold]

sns.set(style='whitegrid')


def plot_h(dataframe, x, title, label):
    plt.figure(figsize=(10, 5))
    sns.histplot(dataframe[x], bins=50, kde=True)
    plt.title(title)
    plt.xlabel(label)
    plt.ylabel('Number of Persons')
    plt.tight_layout()
    plt.show()


def plot_scatter(dataframe, x, y, title, label_x, label_y):
    plt.figure(figsize=(8, 6))
    sns.scatterplot(data=dataframe, x=x, y=y)
    plt.axhline(0, color='gray', linestyle='--', linewidth=1)
    plt.axvline(0, color='gray', linestyle='--', linewidth=1)
    plt.title(title)
    plt.xlabel(label_x)
    plt.ylabel(label_y)
    plt.tight_layout()
    plt.show()


def plot_histograms(dataframe, use_pct_for_plot=True):
    travel_time = 'trav_time_diff'
    travel_time_label = 'Travel Time Difference [h]'
    travel_time_title = 'Distribution of Travel Time Differences per Person'
    distance = 'distance_diff'
    distance_label = 'Distance Difference [km]'
    distance_title = 'Distribution of Distance Differences per Person'

    if use_pct_for_plot:
        travel_time = 'trav_time_pct_change'
        travel_time_label = 'Travel Time Change (%)'
        travel_time_title = 'Percent Change in Travel Time per Person'
        distance = 'distance_pct_change'
        distance_label = 'Distance Change [%]'
        distance_title = 'Percent Change in Distance per Person'

    # Plot histogram of travel time differences
    plot_h(dataframe, travel_time, travel_time_title, travel_time_label)

    # Plot histogram of distance differences
    plot_h(dataframe, distance, distance_title, distance_label)

    # Scatter plot to show relationship
    plot_scatter(dataframe, distance, travel_time, 'Travel Time vs. Distance Differences',
                 distance_label, travel_time_label)


plot_histograms(df)

no_changes_in_trip = df[df['distance_diff'].abs() == 0]
print(f"Number of persons with no changes in trip: {len(no_changes_in_trip)}")
plot_h(no_changes_in_trip, 'trav_time_pct_change',
       'Percent change Travel Time Differences per Person for trips with no Changes',
       'Travel Time Change (%)')

no_changes_in_trip_outlier_threshold = 10  # in %
no_changes_in_trip_outlier = no_changes_in_trip[no_changes_in_trip['trav_time_pct_change'].abs() >
                                                no_changes_in_trip_outlier_threshold]

print(f"Number of persons with more than {no_changes_in_trip_outlier_threshold}% change in travel time and no changes "
      f"in trips: {len(no_changes_in_trip_outlier)}")
print(f"Those Persons: {no_changes_in_trip_outlier['person'].values}")

plot_h(no_changes_in_trip_outlier, 'sum_distance_unmod',
       f'Traveled Distance of Persons with more than {no_changes_in_trip_outlier_threshold}% change in travel time '
       f'and no change in trips',
       'Distance [km]')

plot_scatter(no_changes_in_trip_outlier, 'sum_distance_unmod', 'trav_time_diff',
             f'Travel Time Difference vs. Distance of Persons with more than {no_changes_in_trip_outlier_threshold}% '
             'change in travel time \nand no change in trips',
             'Distance [km]', 'Travel Time Difference [h]')

no_changes_in_trip_norm = no_changes_in_trip[no_changes_in_trip['trav_time_pct_change'].abs() <=
                                             no_changes_in_trip_outlier_threshold]

print(f"Number of persons with less than {no_changes_in_trip_outlier_threshold}% change in travel time and no changes "
      f"in trips: {len(no_changes_in_trip_norm)}")


plot_h(no_changes_in_trip_norm, 'sum_distance_unmod',
       f'Traveled Distance of Persons with less than {no_changes_in_trip_outlier_threshold}% change in travel time '
       f'and no change in trips',
       'Distance [km]')

plot_scatter(no_changes_in_trip_norm, 'sum_distance_unmod', 'trav_time_diff',
             f'Travel Time Difference vs. Distance of Persons with less than {no_changes_in_trip_outlier_threshold}% '
             'change in travel time \nand no change in trips',
             'Distance [km]', 'Travel Time Difference [h]')
