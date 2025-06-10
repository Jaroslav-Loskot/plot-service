import matplotlib.pyplot as plt
import base64
from io import BytesIO

def generate_plot(x_values, y_values):
    plt.figure()
    plt.plot(x_values, y_values, marker='o')
    plt.xlabel("X Axis")
    plt.ylabel("Y Axis")
    plt.title("Matplotlib Line Plot")

    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()  # Important: prevent memory leak
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return img_base64
