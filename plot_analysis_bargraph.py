import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd


lastIteration = 150
modified = True
desiredMaxSpeed = 100
it = lastIteration

affectedPersons = True

# Load the CSV you generated earlier
df_unmodified = pd.read_csv(f"output/{'aP/' if affectedPersons else ''}{False}_mode_comparison_stacked_{it}.csv", index_col=0)
df_modified = pd.read_csv(f"output/{'aP/' if affectedPersons else ''}{True}_mode_comparison_stacked_{it}.csv", index_col=0)


def plot_comparison_row(row_name, title=None, save_path=None):
    modes = df_unmodified.columns

    # Extract values for the given row
    unmod_values = df_unmodified.loc[row_name]
    mod_values = df_modified.loc[row_name]

    # Set up bar positions
    x = range(len(modes))
    bar_width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))

    # Bars
    ax.bar([i - bar_width/2 for i in x], unmod_values, width=bar_width, label='Unmodified', color='gray')
    ax.bar([i + bar_width/2 for i in x], mod_values, width=bar_width, label='Modified', color='skyblue')

    # Axis formatting
    ax.set_xticks(x)
    ax.set_xticklabels(modes, rotation=45, ha='right')
    ax.set_ylabel(row_name)
    ax.set_title(title if title else f"Comparison of {row_name}")
    ax.legend()

    ax.grid(axis='y', linestyle='--', alpha=0.7)

    # Save or show
    if save_path:
        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        plt.close()
    else:
        plt.tight_layout()
        plt.show()


plot_comparison_row("Total time traveled [h]")
plot_comparison_row("Total distance traveled [km]")
plot_comparison_row("Number of trips")
plot_comparison_row("Average speed [km/h]")
plot_comparison_row("Avg. time traveled per trip [h]")
plot_comparison_row("Avg. distance traveled per trip [km]")