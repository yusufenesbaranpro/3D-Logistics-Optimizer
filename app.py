import streamlit as st
import pandas as pd
import json
import xml.etree.ElementTree as ET
from io import BytesIO, StringIO
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
    
    /* File Uploader */
    [data-testid="stFileUploader"] {
        background: rgba(30, 42, 74, 0.3);
        border: 2px dashed rgba(108, 99, 255, 0.3);
        border-radius: 12px;
        padding: 12px;
        transition: border-color 0.3s ease;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(108, 99, 255, 0.6);
    }
    
    /* Import section highlight */
    .import-section {
        background: rgba(30, 42, 74, 0.4);
        border: 1px solid rgba(108, 99, 255, 0.2);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
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


# ─────────────────────────────────────────────────────
# FILE PARSING UTILITIES
# ─────────────────────────────────────────────────────

def parse_csv(file) -> pd.DataFrame:
    """Parse CSV file with auto-detection of separator."""
    content = file.read().decode('utf-8')
    # Try comma first, then semicolon
    for sep in [',', ';', '\t']:
        try:
            df = pd.read_csv(StringIO(content), sep=sep)
            if len(df.columns) >= 3:
                return df
        except Exception:
            continue
    return pd.read_csv(StringIO(content))


def parse_excel(file) -> pd.DataFrame:
    """Parse Excel (.xlsx / .xls) file."""
    return pd.read_excel(file, engine='openpyxl')


def parse_xml(file) -> pd.DataFrame:
    """Parse XML file. Expects <items><item> or <bins><bin> structure."""
    content = file.read().decode('utf-8')
    root = ET.fromstring(content)
    
    records = []
    # Try to find child elements (item, bin, row, record, etc.)
    for child in root:
        record = {}
        for field in child:
            tag = field.tag.strip().lower()
            text = field.text.strip() if field.text else ''
            # Try numeric conversion
            try:
                record[tag] = float(text)
                if record[tag] == int(record[tag]):
                    record[tag] = int(record[tag])
            except (ValueError, TypeError):
                record[tag] = text
        if record:
            records.append(record)
    
    return pd.DataFrame(records)


def parse_json(file) -> pd.DataFrame:
    """Parse JSON file. Expects a list of objects."""
    content = file.read().decode('utf-8')
    data = json.loads(content)
    if isinstance(data, list):
        return pd.DataFrame(data)
    elif isinstance(data, dict):
        # Check for common wrapper keys
        for key in ['items', 'bins', 'data', 'records']:
            if key in data and isinstance(data[key], list):
                return pd.DataFrame(data[key])
        return pd.DataFrame([data])
    return pd.DataFrame()


def parse_uploaded_file(file) -> pd.DataFrame:
    """Route to correct parser based on file extension."""
    name = file.name.lower()
    if name.endswith('.csv'):
        return parse_csv(file)
    elif name.endswith(('.xlsx', '.xls')):
        return parse_excel(file)
    elif name.endswith('.xml'):
        return parse_xml(file)
    elif name.endswith('.json'):
        return parse_json(file)
    else:
        raise ValueError(f"Unsupported file format: {name}")


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names to expected format.
    
    Uses keyword-contains matching so columns like 'Width_cm', 
    'Height_mm', 'Depth_in', 'item_name' are all correctly detected.
    Priority order ensures exact matches win over partial matches.
    """
    # Define mapping rules: (target_name, exact_matches, contains_keywords)
    rules = [
        ('name', 
         {'name', 'item_name', 'item', 'isim', 'ad', 'ürün', 'urun', 'adi', 'adı', 'product', 'label'},
         ['name', 'item', 'isim', 'ürün', 'urun', 'product', 'label', 'adi', 'adı']),
        ('w',    
         {'w', 'width', 'genişlik', 'genislik', 'en'},
         ['width', 'genişlik', 'genislik']),
        ('h',    
         {'h', 'height', 'yükseklik', 'yukseklik', 'boy'},
         ['height', 'yükseklik', 'yukseklik']),
        ('d',    
         {'d', 'depth', 'derinlik', 'uzunluk', 'length'},
         ['depth', 'derinlik', 'uzunluk', 'length']),
        ('qty',  
         {'qty', 'quantity', 'count', 'adet', 'miktar', 'sayi', 'sayı'},
         ['qty', 'quantity', 'count', 'adet', 'miktar', 'sayi', 'sayı']),
        ('weight',
         {'weight', 'agirlik', 'ağırlık'},
         ['weight', 'agirlik', 'ağırlık']),
    ]
    
    col_map = {}
    mapped_targets = set()  # Prevent duplicate mappings
    
    # Pass 1: Exact matches (highest priority)
    for col in df.columns:
        lower = col.strip().lower()
        for target, exact_set, _ in rules:
            if target not in mapped_targets and lower in exact_set:
                col_map[col] = target
                mapped_targets.add(target)
                break
    
    # Pass 2: Contains-keyword matches (for remaining unmapped columns)
    for col in df.columns:
        if col in col_map:
            continue
        lower = col.strip().lower()
        # Remove common suffixes/units for cleaner matching
        cleaned = lower.replace('_', ' ').replace('-', ' ')
        for target, _, keywords in rules:
            if target not in mapped_targets:
                for kw in keywords:
                    if kw in cleaned:
                        col_map[col] = target
                        mapped_targets.add(target)
                        break
                if col in col_map:
                    break
    
    df = df.rename(columns=col_map)
    return df


def validate_items_df(df: pd.DataFrame) -> tuple:
    """Validate DataFrame for item import. Returns (is_valid, message, cleaned_df)."""
    required = ['w', 'h', 'd']
    missing = [c for c in required if c not in df.columns]
    if missing:
        return False, f"Missing required columns: {', '.join(missing)}. Found: {', '.join(df.columns)}", df
    
    # Add defaults
    if 'name' not in df.columns:
        df['name'] = [f"Item {i+1}" for i in range(len(df))]
    if 'qty' not in df.columns:
        df['qty'] = 1
    
    # Convert to numeric
    for col in ['w', 'h', 'd', 'qty']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Drop rows with NaN in critical columns
    before = len(df)
    df = df.dropna(subset=['w', 'h', 'd'])
    dropped = before - len(df)
    
    df['qty'] = df['qty'].fillna(1).astype(int)
    
    msg = f"✅ {len(df)} items ready to import."
    if dropped > 0:
        msg += f" ({dropped} rows skipped due to invalid data)"
    
    return True, msg, df


def validate_bins_df(df: pd.DataFrame) -> tuple:
    """Validate DataFrame for bin import. Returns (is_valid, message, cleaned_df)."""
    required = ['w', 'h', 'd']
    missing = [c for c in required if c not in df.columns]
    if missing:
        return False, f"Missing required columns: {', '.join(missing)}. Found: {', '.join(df.columns)}", df
    
    for col in ['w', 'h', 'd']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    before = len(df)
    df = df.dropna(subset=['w', 'h', 'd'])
    dropped = before - len(df)
    
    msg = f"✅ {len(df)} containers ready to import."
    if dropped > 0:
        msg += f" ({dropped} rows skipped due to invalid data)"
    
    return True, msg, df


# ─────────────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────────────

if 'bins' not in st.session_state:
    st.session_state.bins = []
if 'cargo_items' not in st.session_state:
    st.session_state.cargo_items = [
        {"name": "Box A", "w": 20, "h": 20, "d": 20, "qty": 3},
        {"name": "Box B", "w": 10, "h": 30, "d": 10, "qty": 5},
    ]


# ─────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────

st.title("📦 3D LOGISTICS OPTIMIZER")
st.markdown("*Intelligent 3D bin packing with real-time visualization*")
st.markdown("---")


# ─────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────

with st.sidebar:
    st.header("⚙️ CONFIGURATION")
    
    # ── Manual Input Section ──
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


# ─────────────────────────────────────────────────────
# FILE IMPORT SECTION (Main Area — Top)
# ─────────────────────────────────────────────────────

with st.expander("📁 **Import Data from File** (CSV, Excel, XML, JSON)", expanded=False):
    st.markdown("""
    <div style="
        background: rgba(108, 99, 255, 0.08);
        border-left: 3px solid #6C63FF;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 16px;
        font-size: 0.9rem;
    ">
        <strong>📝 Expected Columns:</strong><br>
        <b>Items:</b> <code>name</code>, <code>w</code> (width), <code>h</code> (height), <code>d</code> (depth), <code>qty</code> (quantity)<br>
        <b>Containers:</b> <code>w</code>, <code>h</code>, <code>d</code><br>
        <em style="color: #7A8599;">Column names are flexible — Turkish names like 'genişlik', 'yükseklik', 'adet' also work.</em>
    </div>
    """, unsafe_allow_html=True)
    
    imp_col1, imp_col2 = st.columns(2)
    
    with imp_col1:
        st.markdown("##### 📦 Import Items")
        items_file = st.file_uploader(
            "Upload items file",
            type=['csv', 'xlsx', 'xls', 'xml', 'json'],
            key='items_uploader',
            help="Supported: CSV, Excel, XML, JSON"
        )
        
        if items_file is not None:
            try:
                df = parse_uploaded_file(items_file)
                df = normalize_columns(df)
                is_valid, msg, df = validate_items_df(df)
                
                if is_valid:
                    st.success(msg)
                    st.dataframe(df, use_container_width=True, height=200)
                    
                    import_mode = st.radio(
                        "Import mode:",
                        ["Append to existing items", "Replace all items"],
                        key="items_import_mode",
                        horizontal=True
                    )
                    
                    if st.button("✅ Import Items", key="btn_import_items", use_container_width=True):
                        new_items = df[['name', 'w', 'h', 'd', 'qty']].to_dict('records')
                        if import_mode == "Replace all items":
                            st.session_state.cargo_items = new_items
                        else:
                            st.session_state.cargo_items.extend(new_items)
                        st.success(f"🎉 {len(new_items)} items imported!")
                        st.rerun()
                else:
                    st.error(msg)
                    st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"❌ Error parsing file: {e}")
    
    with imp_col2:
        st.markdown("##### 🏗️ Import Containers")
        bins_file = st.file_uploader(
            "Upload containers file",
            type=['csv', 'xlsx', 'xls', 'xml', 'json'],
            key='bins_uploader',
            help="Supported: CSV, Excel, XML, JSON"
        )
        
        if bins_file is not None:
            try:
                df = parse_uploaded_file(bins_file)
                df = normalize_columns(df)
                is_valid, msg, df = validate_bins_df(df)
                
                if is_valid:
                    st.success(msg)
                    st.dataframe(df[['w', 'h', 'd']], use_container_width=True, height=200)
                    
                    import_mode = st.radio(
                        "Import mode:",
                        ["Append to existing bins", "Replace all bins"],
                        key="bins_import_mode",
                        horizontal=True
                    )
                    
                    if st.button("✅ Import Containers", key="btn_import_bins", use_container_width=True):
                        new_bins = df[['w', 'h', 'd']].to_dict('records')
                        if import_mode == "Replace all bins":
                            st.session_state.bins = new_bins
                        else:
                            st.session_state.bins.extend(new_bins)
                        st.success(f"🎉 {len(new_bins)} containers imported!")
                        st.rerun()
                else:
                    st.error(msg)
                    st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"❌ Error parsing file: {e}")

st.markdown("---")

# ─────────────────────────────────────────────────────
# MAIN AREA
# ─────────────────────────────────────────────────────

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
        st.info("No items added. Use the sidebar or import a file.")
        
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
