import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO

def generate_plot(
    x=None,
    y=None,
    z=None,
    chart_type="line",
    title=None,
    xlabel=None,
    ylabel=None,
    grid=False,
    series_labels=None
):
    plt.figure()
    ax = plt.gca()

    if chart_type == "line":
        # Support for multiple series (2D y) or single series
        if isinstance(y, list) and all(isinstance(val, list) for val in y):
            for idx, y_series in enumerate(y):
                label = series_labels[idx] if series_labels and idx < len(series_labels) else f"Series {idx + 1}"
                ax.plot(x, y_series, marker='o', label=label)
        else:
            label = series_labels[0] if series_labels else "Line"
            ax.plot(x, y, marker='o', label=label)

    elif chart_type == "bar":
        if isinstance(y[0], list):
            # Multiple series → grouped bar chart
            n_series = len(y)
            n_points = len(x)
            bar_width = 0.8 / n_series
            x_indices = np.arange(n_points)

            for idx, y_series in enumerate(y):
                offset = (idx - (n_series - 1) / 2) * bar_width
                label = series_labels[idx] if series_labels and idx < len(series_labels) else f"Series {idx + 1}"
                ax.bar(x_indices + offset, y_series, width=bar_width, label=label)

            ax.set_xticks(x_indices)
            ax.set_xticklabels(x)
        else:
            label = series_labels[0] if series_labels else "Bar"
            ax.bar(x, y, label=label)

    elif chart_type == "scatter":
        ax.scatter(x, y, label=series_labels[0] if series_labels else "Scatter")

    elif chart_type == "pie":
        labels = series_labels if series_labels else [f"Slice {i+1}" for i in range(len(y))]
        ax.pie(y, labels=labels, autopct="%1.1f%%", startangle=90)
        ax.axis("equal")  # Makes the pie circular

    elif chart_type == "heatmap":
        if z is None:
            raise ValueError("Heatmap requires 'z' matrix data.")
        heatmap = ax.imshow(z, cmap='viridis')
        plt.colorbar(heatmap)

    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")

    # Common plot decorations (not for pie)
    if chart_type != "pie":
        if xlabel:
            ax.set_xlabel(xlabel)
        if ylabel:
            ax.set_ylabel(ylabel)
        if title:
            ax.set_title(title)
        if grid:
            ax.grid(True)
        if chart_type != "heatmap":
            ax.legend()

    # Finalize image and return as bytes
    buf = BytesIO()
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    return buf.read()
