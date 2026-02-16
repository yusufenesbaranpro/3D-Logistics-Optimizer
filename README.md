# 📦 3D Logistics Optimizer

A professional 3D Bin Packing optimization application built with Python and Streamlit.
Uses a heuristic **First Fit Decreasing** algorithm with 6-axis rotation support to pack items into containers efficiently.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red?logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.0+-purple?logo=plotly&logoColor=white)

## ✨ Features

- **3D Visualization**: Interactive 3D view of packed bins using Plotly with distinct colors per item.
- **Algorithm**: Custom First Fit Decreasing with full 6-axis rotation support.
- **File Import**: Bulk import items & containers from **CSV, Excel (.xlsx), XML, JSON** files.
- **Smart Column Detection**: Automatically recognizes column names in both English and Turkish.
- **Modern UI**: Midnight Blue theme with gradient accents and smooth animations.
- **Functionality**:
    - Multiple Items with dimensions and quantities.
    - Multiple configurable container types.
    - Volume Utilization efficiency metrics.
    - Append or Replace import modes.

## 🚀 Installation

1. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## ▶️ Running the App

```bash
streamlit run app.py
```

## 📁 File Import Format

### Items (CSV example)
```csv
name,w,h,d,qty
Laptop Box,40,30,10,4
Monitor Box,60,45,20,2
```

### Containers (CSV example)
```csv
w,h,d
120,80,80
100,60,50
```

> 💡 See the `examples/` folder for sample files in CSV, XML format.

## 📂 Project Structure

| File | Description |
|------|-------------|
| `app.py` | Main Streamlit application, UI, and file import logic |
| `packer.py` | Core packing algorithm (Item, Bin, Packer classes) |
| `visualizer.py` | Plotly 3D visualization with color-coded items |
| `requirements.txt` | Python dependencies |
| `examples/` | Sample import files (CSV, XML) |

## 📝 License

MIT License
