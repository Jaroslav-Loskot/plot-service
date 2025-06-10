import matplotlib.pyplot as plt
import base64
from io import BytesIO

def generate_plot(x_values, y_values, chart_type="line"):
    plt.figure()

    if chart_type == "line":
        plt.plot(x_values, y_values, marker='o')
    elif chart_type == "bar":
        plt.bar(x_values, y_values)
    elif chart_type == "scatter":
        plt.scatter(x_values, y_values)
    elif chart_type == "pie":
        plt.pie(y_values, labels=x_values, autopct='%1.1f%%')
    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")

    if chart_type != "pie":
        plt.xlabel("X Axis")
        plt.ylabel("Y Axis")
        plt.title(f"{chart_type.capitalize()} Plot")

    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')
