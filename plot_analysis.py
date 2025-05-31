import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd


lastIteration = 150
modified = False
desiredMaxSpeed = 100
it = lastIteration

affectedPersons = True

# Load the CSV you generated earlier
df = pd.read_csv(f"output/{'aP/' if affectedPersons else ''}{modified}_mode_comparison_stacked_{it}.csv", index_col=0)

# Optional: round the values for cleaner appearance
rounded_df = df.copy()
for col in rounded_df.columns:
    # Round all float values to 2 decimals
    rounded_df[col] = pd.to_numeric(rounded_df[col], errors='coerce').round(1)

# Setup
n_rows, n_cols = rounded_df.shape
fig, ax = plt.subplots(figsize=(n_cols * 1.5 + 2, n_rows * 0.6 + 1))  # adjust sizing
ax.axis('off')

# Define zebra colors
row_colors = [mcolors.to_rgba('whitesmoke'), mcolors.to_rgba('lightgrey')]

# Create the table
table = ax.table(
    cellText=rounded_df.values,
    rowLabels=rounded_df.index,
    colLabels=rounded_df.columns,
    cellLoc='center',
    rowLoc='center',
    loc='center'
)

# Styling
table.auto_set_font_size(False)
table.set_fontsize(11)
table.scale(1.2, 1.2)

# Iterate over cells to apply styles
for (row, col), cell in table.get_celld().items():
    # Header row
    if row == 0 or col == -1:
        cell.set_text_props(weight='bold', color='black')
        cell.set_facecolor('#d0d0d0')  # header gray
    # Data cells
    else:
        cell.set_facecolor(row_colors[0])
        cell.set_edgecolor('gray')
        if col == -1:  # row labels
            cell.set_text_props(ha='left', weight='bold')

# Save as PNG
plt.savefig(f"output/{'aP/' if affectedPersons else ''}{modified}_mode_comparison_stacked_{it}.png", bbox_inches='tight', dpi=300)
plt.close()

