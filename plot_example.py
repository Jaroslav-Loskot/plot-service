import matplotlib.pyplot as plt
from io import BytesIO

def generate_plot(x=None, y=None, z=None, chart_type="line", title=None, xlabel=None, ylabel=None, grid=False, series_labels=None):
    plt.figure()
    ax = plt.gca()

    if chart_type == "line":
        if y is None or x is None:
            raise ValueError("Both 'x' and 'y' must be provided for line charts.")
        
        # Detect 2D: multiple lines
        if isinstance(y, list) and all(isinstance(val, list) for val in y):
            for idx, y_series in enumerate(y):
                if len(y_series) != len(x):
                    raise ValueError(f"Length of x ({len(x)}) does not match length of y[{idx}] ({len(y_series)}).")
                label = series_labels[idx] if series_labels and idx < len(series_labels) else f"Series {idx + 1}"
                ax.plot(x, y_series, marker='o', label=label)
        elif isinstance(y, list):
            if len(y) != len(x):
                raise ValueError(f"Length of x ({len(x)}) does not match length of y ({len(y)}).")
            label = series_labels[0] if series_labels else "Line"
            ax.plot(x, y, marker='o', label=label)
        else:
            raise ValueError("Invalid 'y' format: expected list or list of lists for line chart.")

    elif chart_type == "bar":
        if x is None or y is None or len(x) != len(y):
            raise ValueError("Bar chart requires 'x' and 'y' of the same length.")
        ax.bar(x, y, label="Bar")

    elif chart_type == "scatter":
        if x is None or y is None or len(x) != len(y):
            raise ValueError("Scatter chart requires 'x' and 'y' of the same length.")
        ax.scatter(x, y, label="Scatter")

    elif chart_type == "pie":
        if y is None:
            raise ValueError("Pie chart requires 'y' values.")
        ax.pie(y, labels=x, autopct='%1.1f%%')

    elif chart_type == "heatmap":
        if z is None:
            raise ValueError("Heatmap requires 'z' matrix data.")
        heatmap = ax.imshow(z, cmap='viridis')
        plt.colorbar(heatmap)

    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")

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

    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return buf.read()
