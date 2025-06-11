import matplotlib.pyplot as plt
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
        if isinstance(y, list) and all(isinstance(val, list) for val in y):
            for idx, y_series in enumerate(y):
                label = series_labels[idx] if series_labels and idx < len(series_labels) else f"Series {idx + 1}"
                ax.plot(x, y_series, marker='o', label=label)
        else:
            label = series_labels[0] if series_labels else "Line"
            ax.plot(x, y, marker='o', label=label)

    elif chart_type == "bar":
        ax.bar(x, y, label=series_labels[0] if series_labels else "Bar")

    elif chart_type == "scatter":
        ax.scatter(x, y, label=series_labels[0] if series_labels else "Scatter")

    elif chart_type == "pie":
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
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    return buf.read()
