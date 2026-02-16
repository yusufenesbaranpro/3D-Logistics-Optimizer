import streamlit as st
import pandas as pd
from packer import Item, Bin, Packer
from visualizer import visualize_bin
import plotly.graph_objects as go

# Set page config
st.set_page_config(layout="wide", page_title="3D Bin Packer", page_icon="📦", initial_sidebar_state="expanded")

# Custom CSS for Braun Aesthetic
st.markdown("""
<style>
    /* Global Background and Text */
    .stApp {
        background-color: #000000;
        color: #FFFFFF;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #111111;
        border-right: 1px solid #333333;
    }
    
    /* Inputs */
    .stTextInput input, .stNumberInput input {
        color: #FFFFFF;
        background-color: #222222;
        border: 1px solid #444444;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #FFFFFF;
        color: #000000;
        border: none;
        border-radius: 0px; /* Sharp edges for Braun look */
        font-weight: bold;
        padding: 0.5rem 1rem;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background-color: #DDDDDD;
        color: #000000;
        border: 1px solid #FFFFFF;
    }
    
    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF !important;
        font-weight: 300;
        letter-spacing: -0.5px;
    }
    
    /* Tables */
    [data-testid="stDataFrame"] {
        background-color: #111111;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #000000;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #111111;
        border-radius: 0px;
        color: #888888;
        font-weight: 400;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF;
        color: #000000;
        font-weight: 600;
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

st.title("3D BIN PACKER")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("CONFIGURATION")
    
    st.subheader("1. Container (Bin)")
    bin_w = st.number_input("Width", min_value=1.0, value=100.0, key='bin_w')
    bin_h = st.number_input("Height", min_value=1.0, value=50.0, key='bin_h')
    bin_d = st.number_input("Depth", min_value=1.0, value=50.0, key='bin_d')
    
    if st.button("Add Bin Type"):
        st.session_state.bins.append({"w": bin_w, "h": bin_h, "d": bin_d})
        st.success("Bin added.")

    st.markdown("---")
    
    st.subheader("2. Items")
    item_name = st.text_input("Item Name", value="Item X")
    col1, col2, col3 = st.columns(3)
    with col1: i_w = st.number_input("W", min_value=1.0, value=10.0)
    with col2: i_h = st.number_input("H", min_value=1.0, value=10.0)
    with col3: i_d = st.number_input("D", min_value=1.0, value=10.0)
    qty = st.number_input("Quantity", min_value=1, value=1)
    
    if st.button("Add Item"):
        st.session_state.cargo_items.append({
            "name": item_name, "w": i_w, "h": i_h, "d": i_d, "qty": qty
        })
        st.success(f"{qty}x {item_name} added.")
        
    if st.button("Clear All"):
        st.session_state.cargo_items = []
        st.session_state.bins = []
        st.rerun()

# Main Area
col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader("Inventory")
    if st.session_state.cargo_items:
        try:
            df = pd.DataFrame(st.session_state.cargo_items)
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Error displaying items: {e}")
            st.write("Raw items data:", st.session_state.cargo_items)
    else:
        st.info("No items added.")
        
    st.subheader("Containers Type List")
    # Always include the current input bin as default if list is empty?
    # Or just use the sidebar inputs as a single bin type if list is empty.
    if not st.session_state.bins:
        st.info(f"Using default bin: {bin_w}x{bin_h}x{bin_d}")
    else:
        st.dataframe(pd.DataFrame(st.session_state.bins), use_container_width=True)

    pack_btn = st.button("RUN OPTIMIZATION", use_container_width=True)

with col_right:
    if pack_btn:
        packer = Packer()
        
        # Add Bins
        # Logic: If bins list is empty, use the one from inputs. 
        # But usually bin packing implies we have ONE bin type and want to see how many we need,
        # OR we have multiple bin types and want to fit into best.
        # User said: "Multiple Bins/Containers".
        # Let's assume we want to pack all items.
        # We will add infinite bins of the specified types? 
        # Or just the bins provided. 
        # Let's assume "Pack into these bins". If items don't fit, they remain unpacked.
        
        bin_sources = st.session_state.bins if st.session_state.bins else [{"w": bin_w, "h": bin_h, "d": bin_d}]
        
        # ISSUE: Packer logic iterates bins once.
        # If we need multiple bins of same size, we should add them.
        # For this MVU, let's just add 1 of each defined bin type. 
        # If user wants multiple, they define multiple or we assume infinite?
        # Let's assume user defines the *available* bins. 
        # But typically users want "How many bins do I need?".
        # "First Fit Decreasing" often implies adding new bins as needed.
        # Let's add 5 empty bins of the FIRST type defined (or current inputs) to ensure space.
        # Or better: Just add the bins the user added.
        
        for b in bin_sources:
            # We add 1 bin of this type.
            # Maybe the user implies "Types".
            # Let's add 5 of each type to be safe? 
            # Complex. Let's stick to: "Defined Bins are the Available Bins".
            for _ in range(1): # Just 1 for now unless user adds more
                 packer.add_bin(Bin("Bin", b['w'], b['h'], b['d']))
        
        # Strategy: If user didn't add any bins to the list but defined one in inputs, use that.
        if not st.session_state.bins:
             # Add a few bins of this size to accommodate items
             for i in range(5):
                 packer.add_bin(Bin(f"Bin {i+1}", bin_w, bin_h, bin_d))
        else:
             # Add defined bins
             for i, b in enumerate(st.session_state.bins):
                 packer.add_bin(Bin(f"Bin {i+1}", b['w'], b['h'], b['d']))

        # Add Items
        for item in st.session_state.cargo_items:
            for _ in range(item['qty']):
                packer.add_item(Item(item['name'], item['w'], item['h'], item['d']))
        
        # Pack
        packer.pack(bigger_first=True)
        

        # Display Results
        st.subheader("Packing Results")
        
        # Display Unfitted Items globally
        if packer.unfit_items:
             st.error(f"⚠️ {len(packer.unfit_items)} items could not be packed into any bin.")
             with st.expander("Show Unfitted Items"):
                 st.dataframe(pd.DataFrame([{'Name': i.name, 'Vol': i.get_volume()} for i in packer.unfit_items]))
        
        if not packer.bins:
            st.warning("No bins created.")
        else:
            tabs = st.tabs([b.name for b in packer.bins])
            
            for i, bin_obj in enumerate(packer.bins):
                with tabs[i]:
                    # Stats
                    total_vol = bin_obj.get_volume()
                    packed_vol = sum([it.get_volume() for it in bin_obj.items])
                    efficiency = (packed_vol / total_vol) * 100 if total_vol > 0 else 0
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Items Packed", len(bin_obj.items))
                    c2.metric("Volume Utilization", f"{efficiency:.2f}%")
                    c3.metric("Bin Volume", f"{total_vol:.0f}")
                    
                    # Visualization
                    if len(bin_obj.items) > 0:
                        fig = visualize_bin(bin_obj)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Bin is empty.")
                    
