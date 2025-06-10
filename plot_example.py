import matplotlib.pyplot as plt
import base64
from io import BytesIO

def generate_plot(x_values, y_values, chart_type="line", title=None, xlabel=None, ylabel=None, grid=False):
    plt.figure()

    if chart_type == "line":
        plt.plot(x_values, y_values, marker='o', label="Line")
    elif chart_type == "bar":
        plt.bar(x_values, y_values, label="Bar")
    elif chart_type == "scatter":
        plt.scatter(x_values, y_values, label="Scatter")
    elif chart_type == "pie":
        plt.pie(y_values, labels=x_values, autopct='%1.1f%%')
    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")

    if chart_type != "pie":
        if xlabel:
            plt.xlabel(xlabel)
        if ylabel:
            plt.ylabel(ylabel)
        if title:
            plt.title(title)
        if grid:
            plt.grid(True)
        plt.legend()

    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return buf.read()  # return raw image bytes

