# 3D Bin Packing Optimization App

This is a professional 3D Bin Packing optimization application built with Python and Streamlit.
It uses a heuristic "First Fit Decreasing" algorithm with 6-axis rotation support to pack items into containers efficiently.

## Features
- **3D Visualization**: Interactive 3D view of packed bins using Plotly.
- **Algorithm**: Custom implementation of First Fit Decreasing with rotation support.
- **UI**: Minimalist "Braun" aesthetic (High Contrast Black & White).
- **Functionality**:
    - Multiple Items with dimensions and quantities.
    - Configurable Bin dimensions.
    - Efficiency calculation (Volume Utilization).

## Installation

1. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the App

Run the Streamlit app:
```bash
streamlit run app.py
```

## Structure
- `app.py`: Main Streamlit application and UI logic.
- `packer.py`: Core packing algorithm (Item, Bin, Packer classes).
- `visualizer.py`: Plotly visualization logic for 3D rendering.
