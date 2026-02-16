import streamlit as st
import pandas as pd
from packer import Item, Bin, Packer
from visualizer import visualize_bin
import plotly.graph_objects as go

# Set page config
st.set_page_config(layout="wide", page_title="3D Logistics Optimizer", page_icon="📦", initial_sidebar_state="expanded")

# Custom CSS — Midnight Blue Theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Background and Text */
    .stApp {
        background: linear-gradient(135deg, #0F1629 0%, #1A1F3A 50%, #0F1629 100%);
        color: #E0E6F0;
        font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1A2340 0%, #141D35 100%);
        border-right: 1px solid rgba(108, 99, 255, 0.2);
    }
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        background: linear-gradient(90deg, #6C63FF, #00D2FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Inputs */
    .stTextInput input, .stNumberInput input {
        color: #E0E6F0 !important;
        background-color: #1E2A4A !important;
        border: 1px solid rgba(108, 99, 255, 0.3) !important;
        border-radius: 8px !important;
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
    }
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #6C63FF !important;
        box-shadow: 0 0 0 2px rgba(108, 99, 255, 0.2) !important;
    }
    
    /* Primary Action Button */
    .stButton > button {
        background: linear-gradient(135deg, #6C63FF, #00D2FF) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.5rem !important;
        letter-spacing: 0.5px;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(108, 99, 255, 0.3) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(108, 99, 255, 0.5) !important;
        background: linear-gradient(135deg, #7B73FF, #1ADBFF) !important;
    }
    .stButton > button:active {
        transform: translateY(0px) !important;
    }
    
    /* Headings */
    h1 {
        background: linear-gradient(90deg, #6C63FF, #00D2FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    h2, h3 {
        color: #C8D0E0 !important;
        font-weight: 500 !important;
    }
    h4, h5, h6 {
        color: #A0AABB !important;
        font-weight: 400 !important;
    }
    
    /* Tables / DataFrames */
    [data-testid="stDataFrame"] {
        background-color: rgba(26, 35, 64, 0.6);
        border-radius: 8px;
        border: 1px solid rgba(108, 99, 255, 0.15);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: rgba(30, 42, 74, 0.5);
        border-radius: 8px 8px 0 0;
        color: #7A8599;
        font-weight: 500;
        border: 1px solid rgba(108, 99, 255, 0.1);
        border-bottom: none;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(108, 99, 255, 0.2), rgba(0, 210, 255, 0.15)) !important;
        color: #FFFFFF !important;
        font-weight: 600;
        border: 1px solid rgba(108, 99, 255, 0.3);
        border-bottom: none;
    }
    
    /* Metrics */
    [data-testid="stMetric"] {
        background: rgba(30, 42, 74, 0.5);
        border: 1px solid rgba(108, 99, 255, 0.15);
        border-radius: 12px;
        padding: 16px 20px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(108, 99, 255, 0.15);
    }
    [data-testid="stMetricLabel"] {
        color: #7A8599 !important;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-weight: 700;
    }
    
    /* Divider */
    hr {
        border-color: rgba(108, 99, 255, 0.15) !important;
    }
    
    /* Alert boxes */
    .stAlert {
        border-radius: 8px;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: rgba(30, 42, 74, 0.5);
        border-radius: 8px;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #0F1629;
    }
    ::-webkit-scrollbar-thumb {
        background: #2A3560;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #6C63FF;
    }
    
</style>
""", unsafe_allow_html=True)

# Function to initialize session state
if 'bins' not in st.session_state:
    st.session_state.bins = [] # List of dicts
if 'cargo_items' not in st.session_state:
    # Pre-populate with some examples
    st.session_state.cargo_items = [
        {"name": "Box A", "w": 20, "h": 20, "d": 20, "qty": 3},
        {"name": "Box B", "w": 10, "h": 30, "d": 10, "qty": 5},
    ]

st.title("📦 3D LOGISTICS OPTIMIZER")
st.markdown("*Intelligent 3D bin packing with real-time visualization*")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ CONFIGURATION")
    
    st.subheader("1. Container (Bin)")
    bin_w = st.number_input("Width", min_value=1.0, value=100.0, key='bin_w')
    bin_h = st.number_input("Height", min_value=1.0, value=50.0, key='bin_h')
    bin_d = st.number_input("Depth", min_value=1.0, value=50.0, key='bin_d')
    
    if st.button("➕ Add Bin Type", use_container_width=True):
        st.session_state.bins.append({"w": bin_w, "h": bin_h, "d": bin_d})
        st.success("✅ Bin added.")

    st.markdown("---")
    
    st.subheader("2. Items")
    item_name = st.text_input("Item Name", value="Item X")
    col1, col2, col3 = st.columns(3)
    with col1: i_w = st.number_input("W", min_value=1.0, value=10.0)
    with col2: i_h = st.number_input("H", min_value=1.0, value=10.0)
    with col3: i_d = st.number_input("D", min_value=1.0, value=10.0)
    qty = st.number_input("Quantity", min_value=1, value=1)
    
    if st.button("➕ Add Item", use_container_width=True):
        st.session_state.cargo_items.append({
            "name": item_name, "w": i_w, "h": i_h, "d": i_d, "qty": qty
        })
        st.success(f"✅ {qty}x {item_name} added.")
    
    st.markdown("---")
        
    if st.button("🗑️ Clear All", use_container_width=True):
        st.session_state.cargo_items = []
        st.session_state.bins = []
        st.rerun()

# Main Area
col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader("📋 Inventory")
    if st.session_state.cargo_items:
        try:
            df = pd.DataFrame(st.session_state.cargo_items)
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Error displaying items: {e}")
            st.write("Raw items data:", st.session_state.cargo_items)
    else:
        st.info("No items added. Use the sidebar to add items.")
        
    st.subheader("🏗️ Container Types")
    if not st.session_state.bins:
        st.info(f"Using default bin: {bin_w} × {bin_h} × {bin_d}")
    else:
        st.dataframe(pd.DataFrame(st.session_state.bins), use_container_width=True)

    pack_btn = st.button("🚀 RUN OPTIMIZATION", use_container_width=True)

with col_right:
    if pack_btn:
        packer = Packer()
        
        bin_sources = st.session_state.bins if st.session_state.bins else [{"w": bin_w, "h": bin_h, "d": bin_d}]
        
        for b in bin_sources:
            for _ in range(1):
                 packer.add_bin(Bin("Bin", b['w'], b['h'], b['d']))
        
        if not st.session_state.bins:
             for i in range(5):
                 packer.add_bin(Bin(f"Bin {i+1}", bin_w, bin_h, bin_d))
        else:
             for i, b in enumerate(st.session_state.bins):
                 packer.add_bin(Bin(f"Bin {i+1}", b['w'], b['h'], b['d']))

        # Add Items
        for item in st.session_state.cargo_items:
            for _ in range(item['qty']):
                packer.add_item(Item(item['name'], item['w'], item['h'], item['d']))
        
        # Pack
        packer.pack(bigger_first=True)
        
        # Display Results
        st.subheader("📊 Packing Results")
        
        # Display Unfitted Items globally
        if packer.unfit_items:
             st.error(f"⚠️ {len(packer.unfit_items)} items could not be packed into any bin.")
             with st.expander("Show Unfitted Items"):
                 st.dataframe(pd.DataFrame([{'Name': i.name, 'Vol': i.get_volume()} for i in packer.unfit_items]))
        
        if not packer.bins:
            st.warning("No bins created.")
        else:
            tabs = st.tabs([f"📦 {b.name}" for b in packer.bins])
            
            for i, bin_obj in enumerate(packer.bins):
                with tabs[i]:
                    # Stats
                    total_vol = bin_obj.get_volume()
                    packed_vol = sum([it.get_volume() for it in bin_obj.items])
                    efficiency = (packed_vol / total_vol) * 100 if total_vol > 0 else 0
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("📦 Items Packed", len(bin_obj.items))
                    c2.metric("📈 Volume Utilization", f"{efficiency:.1f}%")
                    c3.metric("📐 Bin Volume", f"{total_vol:,.0f}")
                    
                    # Visualization
                    if len(bin_obj.items) > 0:
                        fig = visualize_bin(bin_obj)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Bin is empty.")
    else:
        # Show placeholder when no optimization has run
        st.markdown("""
        <div style="
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 400px;
            border: 2px dashed rgba(108, 99, 255, 0.3);
            border-radius: 16px;
            background: rgba(30, 42, 74, 0.2);
        ">
            <p style="font-size: 3rem; margin: 0;">📦</p>
            <p style="color: #7A8599; font-size: 1.1rem; margin-top: 12px;">
                Add items & containers, then click <strong style="color: #6C63FF;">RUN OPTIMIZATION</strong>
            </p>
            <p style="color: #4A5568; font-size: 0.85rem;">
                Results and 3D visualization will appear here
            </p>
        </div>
        """, unsafe_allow_html=True)
