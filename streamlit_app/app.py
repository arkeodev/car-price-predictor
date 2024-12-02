import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime
import time
import os
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
import logging

load_dotenv()

API_URL = os.getenv('API_URL', "http://localhost:8000")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Car Price Predictor",
    page_icon="🚗",
    layout="wide"
)

st.markdown("""
    <style>
        .stMetric {
            background-color: #f0f2f6;
            padding: 10px;
            border-radius: 5px;
        }
        .stAlert {
            padding: 10px;
            border-radius: 5px;
        }
        .prediction-box {
            background-color: #e6f3ff;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
        }
        .footer {
            text-align: center;
            padding: 20px;
            position: fixed;
            bottom: 0;
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def fetch_cars() -> pd.DataFrame:
    """
    Fetch cars data from API with caching
    
    Returns:
        pd.DataFrame: DataFrame containing car listings
    """
    try:
        logger.info("Fetching data from API...")
        response = requests.get(f"{API_URL}/cars", timeout=10)
        response.raise_for_status()
        
        data = pd.DataFrame(response.json())
        logger.info(f"Successfully fetched {len(data)} records")
        return data
        
    except requests.exceptions.Timeout:
        logger.error("API request timed out")
        st.error("Server is taking too long to respond. Please try again.")
    except requests.exceptions.ConnectionError:
        logger.error("Failed to connect to API")
        st.error("Could not connect to server. Please check if it's running.")
    except Exception as e:
        logger.error(f"Unexpected error fetching data: {str(e)}")
        st.error("An unexpected error occurred while fetching data.")
    
    return pd.DataFrame()

@st.cache_data(ttl=600)
def get_unique_values(df: pd.DataFrame, column: str) -> List[Any]:
    """
    Get unique values from DataFrame column
    
    Args:
        df: Input DataFrame
        column: Column name to get unique values from
        
    Returns:
        List of unique values from the column
    """
    try:
        return sorted(df[column].unique().tolist()) if not df.empty else []
    except Exception as e:
        logger.error(f"Error getting unique values for {column}: {str(e)}")
        return []

def create_plot(df: pd.DataFrame, plot_type: str) -> Optional[px.Figure]:
    """
    Create different types of plots based on the data
    
    Args:
        df: Input DataFrame
        plot_type: Type of plot to create
        
    Returns:
        Plotly figure object or None if creation fails
    """
    try:
        if df.empty:
            return None
            
        if plot_type == "distribution":
            fig = px.histogram(
                df,
                x="price",
                title="Price Distribution",
                nbins=30,
                labels={"price": "Price ($)", "count": "Number of Cars"}
            )
            fig.update_layout(showlegend=False)
            
        elif plot_type == "scatter":
            fig = px.scatter(
                df[df['price'].notna()],  
                x="mileage",
                y="price",
                color="model",
                size="engine_size",
                title="Price vs Mileage by Model",
                labels={
                    "mileage": "Mileage (miles)",
                    "price": "Price ($)",
                    "model": "Model",
                    "engine_size": "Engine Size (L)"
                }
            )
            
        elif plot_type == "box":
            fig = px.box(
                df[df['price'].notna()],  
                x="year",
                y="price",
                title="Price Distribution by Year",
                labels={"year": "Year", "price": "Price ($)"}
            )
            
        elif plot_type == "prediction":
            valid_data = df[df['price'].notna() & df['predicted_price'].notna()]
            if not valid_data.empty:
                fig = px.scatter(
                    valid_data,
                    x="price",
                    y="predicted_price",
                    color="model",
                    title="Predicted vs Actual Price",
                    labels={
                        "price": "Actual Price ($)",
                        "predicted_price": "Predicted Price ($)",
                        "model": "Model"
                    }
                )
                
                min_val = min(valid_data['price'].min(), valid_data['predicted_price'].min())
                max_val = max(valid_data['price'].max(), valid_data['predicted_price'].max())
                fig.add_shape(
                    type='line',
                    line=dict(dash='dash', color='gray'),
                    x0=min_val,
                    y0=min_val,
                    x1=max_val,
                    y1=max_val
                )
                return fig
            return None
                
        return fig
    except Exception as e:
        logger.error(f"Error creating {plot_type} plot: {str(e)}")
        return None

st.title("🚗 Car Price Predictor")

with st.sidebar:
    st.header("Add New Car")
    
    with st.form("car_form", clear_on_submit=True):
        model = st.text_input(
            "Model",
            help="Enter the car model (e.g., Ford Fiesta)"
        )
        year = st.number_input(
            "Year",
            min_value=1900,
            max_value=datetime.now().year,
            value=2020,
            help="Select the manufacturing year"
        )
        transmission = st.selectbox(
            "Transmission",
            ["Manual", "Automatic", "Semi-Auto"],
            help="Select the transmission type"
        )
        fuel_type = st.selectbox(
            "Fuel Type",
            ["Petrol", "Diesel", "Hybrid", "Electric"],
            help="Select the fuel type"
        )
        mileage = st.number_input(
            "Mileage",
            min_value=0,
            value=10000,
            help="Enter the total mileage in miles"
        )
        engine_size = st.number_input(
            "Engine Size (L)",
            min_value=0.1,
            max_value=10.0,
            value=1.5,
            step=0.1,
            help="Enter the engine size in liters"
        )
        tax = st.number_input(
            "Tax ($)",
            min_value=0,
            value=150,
            help="Enter the annual road tax"
        )
        mpg = st.number_input(
            "MPG",
            min_value=0.0,
            value=50.0,
            help="Enter the miles per gallon"
        )
        price = st.number_input(
            "Price ($)",
            min_value=0,
            value=15000,
            help="Enter the car price"
        )
        
        submitted = st.form_submit_button("Add Car")
        confirmation = st.checkbox("I confirm all details are correct")
        
        if submitted and model and confirmation:
            car_data = {
                "model": model,
                "year": year,
                "transmission": transmission,
                "fueltype": fuel_type,
                "mileage": mileage,
                "engine_size": engine_size,
                "tax": tax,
                "mpg": mpg,
                "price": price
            }
            
            with st.spinner('Adding car...'):
                try:
                    st.write("Attempting to connect to API...")
                    st.write(f"Sending data: {car_data}")
                    response = requests.post(f"{API_URL}/cars", json=car_data)
                    st.write(f"Response status: {response.status_code}")
                    st.write(f"Response content: {response.text}")
                    if response.status_code == 200:
                        st.success("Car added successfully!")
                        st.balloons()
                        fetch_cars.clear()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"Failed to add car: {response.text}")
                except Exception as e:
                    st.error(f"Failed to connect to server: {str(e)}")

df = fetch_cars()

if not df.empty:
    st.subheader("📊 Dashboard Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Cars", len(df))
    
    with col2:
        valid_prices = df['price'].dropna()
        if not valid_prices.empty:
            st.metric("Average Price", f"${valid_prices.mean():,.2f}")
        else:
            st.metric("Average Price", "N/A")
    
    with col3:
        if 'predicted_price' in df.columns:
            valid_predictions = df['predicted_price'].dropna()
            if not valid_predictions.empty:
                st.metric("Average Predicted Price", 
                         f"${valid_predictions.mean():,.2f}")
            else:
                st.metric("Average Predicted Price", "Pending")
    
    with col4:
        valid_prices = df['price'].dropna()
        if not valid_prices.empty:
            st.metric("Price Range", 
                     f"${valid_prices.min():,.0f} - ${valid_prices.max():,.0f}")
        else:
            st.metric("Price Range", "N/A")
    
    st.subheader("📈 Price Analysis")
    tab1, tab2, tab3, tab4 = st.tabs([
        "Price Distribution",
        "Price vs Mileage",
        "Price by Year",
        "Prediction Analysis"
    ])
    
    with tab1:
        fig = create_plot(df, "distribution")
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        fig = create_plot(df, "scatter")
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        fig = create_plot(df, "box")
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        fig = create_plot(df, "prediction")
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("🚗 Car Listings")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        models = get_unique_values(df, 'model')
        model_filter = st.multiselect("Filter by Model", options=models)
    
    with col2:
        min_year = int(df['year'].min())
        max_year = int(df['year'].max())
        if min_year == max_year:
            year_filter = (min_year, min_year)
            st.info(f"Only cars from {min_year}")
        else:
            year_filter = st.slider(
                "Filter by Year",
                min_value=min_year,
                max_value=max_year,
                value=(min_year, max_year)
            )
    
    with col3:
        fuel_types = get_unique_values(df, 'fueltype')
        fuel_filter = st.multiselect("Filter by Fuel Type", options=fuel_types)
    
    filtered_df = df.copy()
    if model_filter:
        filtered_df = filtered_df[filtered_df['model'].isin(model_filter)]
    filtered_df = filtered_df[
        (filtered_df['year'] >= year_filter[0]) &
        (filtered_df['year'] <= year_filter[1])
    ]
    if fuel_filter:
        filtered_df = filtered_df[filtered_df['fueltype'].isin(fuel_filter)]
    
    if not filtered_df.empty:
        display_df = filtered_df[[
            'model', 'year', 'price', 'predicted_price', 'mileage',
            'transmission', 'fueltype', 'mpg', 'engine_size'
        ]].copy()
        
        st.dataframe(
            display_df.style.format({
                'price': lambda x: f'${x:,.2f}' if pd.notnull(x) else 'N/A',
                'predicted_price': lambda x: f'${x:,.2f}' if pd.notnull(x) else 'Pending',
                'engine_size': lambda x: f'{x:.1f}L' if pd.notnull(x) else 'N/A',
                'mpg': lambda x: f'{x:.1f}' if pd.notnull(x) else 'N/A',
                'mileage': lambda x: f'{x:,.0f}' if pd.notnull(x) else 'N/A'
            }),
            hide_index=True,
            use_container_width=True
        )
        
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            "📥 Download Data",
            csv,
            "car_data.csv",
            "text/csv",
            key='download-csv'
        )
    else:
        st.info("No cars match the selected filters")
else:
    st.info("No cars in the database. Add some cars to get started!")

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; padding: 10px;'>
        Built with ❤️ using Streamlit | 
        <a href='http://localhost:8000/docs' target='_blank'>API Documentation</a>
    </div>
    """,
    unsafe_allow_html=True
)