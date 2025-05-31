import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

lastIteration = 150
modified = True
desiredMaxSpeed = 100

it = lastIteration
agg = "mean"

base_path = Path("../matsim-kelheim/output")

file_path_modified = base_path / f"modified-s{desiredMaxSpeed}.0-i{lastIteration}" / "kelheim-id.output_links.csv.gz"
file_path_unmodified = base_path / f"unmodified-i{lastIteration}" / "kelheim-id.output_links.csv.gz"

modified_links_path = base_path / f"modified_links-s{desiredMaxSpeed}.0.txt"

sns.set(style='whitegrid')

a = ""


def load_links_data(file_path, modified):
    df_output = pd.read_csv(file_path, sep=';')

    # Filter for links where car is allowed
    df_output = df_output[df_output['modes'].str.contains('car', regex=False)]

    to_numeric_arrays = ["length", "freespeed", "capacity", "lanes", "vol_car", "vol_freight", "allowed_speed"]
    for el in to_numeric_arrays:
        df_output[el] = pd.to_numeric(df_output[el], errors='coerce')

    df_output['freespeed'] = df_output['freespeed'] * 3.6  # m/s in km/h

    freespeed_cap = 100  # in km/h
    df_output["freespeed_cap"] = df_output["freespeed"].apply(lambda x: min(x, freespeed_cap))

    df_output['vol_transport'] = df_output['vol_car'] + df_output['vol_freight']
    df_output_changed = df_output[df_output['link'].isin(modified)]
    df_output_unchanged = df_output[~df_output['link'].isin(modified)]
    return df_output, df_output_changed, df_output_unchanged


def plot_h(dataframe, x, title, label):
    plt.figure(figsize=(10, 5))
    sns.histplot(dataframe[x], bins=50, kde=True)
    plt.title(title)
    plt.xlabel(label)
    plt.ylabel('Number of Links')
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


with open(modified_links_path, 'r') as f:
    modified_links = set(line.strip() for line in f)

df_mod_all, df_mod_changed, df_mod_unchanged = load_links_data(file_path_modified, modified_links)
df_orig_all, df_orig_changed, df_orig_unchanged = load_links_data(file_path_unmodified, modified_links)

print(f"Number of links (where car is allowed): {df_mod_all.size}, number of changed links: {df_mod_changed.size}, "
      f"number of unchanged links: {df_mod_unchanged.size}")


def compare(df_modified, df_orig, cap=True, car=True):
    mode = 'car' if car else 'freight'
    df_comparison = df_orig.merge(df_modified, on="link", suffixes=("_orig", "_mod"))
    df_comparison[f"vol_diff_{mode}"] = df_comparison[f"vol_{mode}_mod"] - df_comparison[f"vol_{mode}_orig"]

    df_comparison["freespeed_orig"] = df_comparison["freespeed_orig"].round(1)
    df_comparison["freespeed_cap_orig"] = df_comparison["freespeed_cap_orig"].round(1)

    group_by = "freespeed_cap_orig" if cap else "freespeed_orig"
    grouped = df_comparison.groupby(group_by)[f"vol_diff_{mode}"].agg(["mean", "median", "count", "sum"])
    print(grouped)

    grouped_orig = df_comparison.groupby(group_by)[f"vol_{mode}_orig"].agg(["sum"])
    print(grouped_orig)

    grouped["sum"].plot(kind="bar")
    plt.title(f"Change in {mode} Volume by Capped Freespeed Group")
    plt.xlabel("Freespeed Group (km/h)")
    plt.ylabel(f"Volume Change ({mode})")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.show()


compare(df_mod_all, df_orig_all)
compare(df_mod_all, df_orig_all, False)
compare(df_mod_all, df_orig_all, True, False)
compare(df_mod_all, df_orig_all, False, False)
#compare(df_mod_changed, df_orig_changed)
#compare(df_mod_unchanged, df_orig_unchanged)




