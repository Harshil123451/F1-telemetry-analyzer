# streamlit_app.py - Web-based F1 Telemetry Analyzer

import streamlit as st
import fastf1
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

# Configure Streamlit page
st.set_page_config(
    page_title="F1 Telemetry Analyzer",
    page_icon="🏎️",
    layout="wide"
)



# Initialize FastF1 cache
@st.cache_resource
def init_cache():
    cache_dir = 'f1_cache'
    os.makedirs(cache_dir, exist_ok=True)
    fastf1.Cache.enable_cache(cache_dir)
    return True

# Initialize session state
if 'session' not in st.session_state:
    st.session_state.session = None
if 'drivers' not in st.session_state:
    st.session_state.drivers = []

init_cache()

# Title and description
st.title("🏎️ F1 Telemetry Analyzer")
st.markdown("""
*Analyze Formula 1 telemetry data with interactive visualizations*
""")

# Sidebar for session selection
st.sidebar.header("🔧 Session Configuration")

with st.sidebar.form("session_form"):
    year = st.selectbox("Year", [2026, 2025, 2024, 2023, 2022, 2021, 2020], index=0)
    grand_prix = st.selectbox("Grand Prix", [
        "Bahrain", "Saudi Arabia", "Australia", "Azerbaijan", "Miami", 
        "Monaco", "Spain", "Canada", "Austria", "Great Britain", 
        "Hungary", "Belgium", "Netherlands", "Italy", "Singapore", 
        "Japan", "Qatar", "United States", "Mexico", "Brazil", "Las Vegas", "Abu Dhabi", "China"
    ])
    session_type = st.selectbox("Session Type", ["R", "Q", "FP1", "FP2", "FP3"])
    load_button = st.form_submit_button("Load Session")

@st.cache_data
def load_session_data(year, grand_prix, session_type):
    """Load F1 session data with caching"""
    try:
        session = fastf1.get_session(year, grand_prix, session_type)
        session.load(telemetry=True)
        return session
    except Exception as e:
        st.error(f"Error loading session: {str(e)}")
        return None

# Load session when button is clicked
if load_button:
    with st.spinner("Loading session data..."):
        st.session_state.session = load_session_data(year, grand_prix, session_type)
        if st.session_state.session:
            st.success("Session loaded successfully!")
            
            # Load driver list
            try:
                drivers = st.session_state.session.drivers
                driver_list = []
                for driver_number in drivers:
                    driver_info = st.session_state.session.get_driver(driver_number)
                    driver_list.append({
                        'number': driver_number,
                        'name': f"{driver_info['FirstName']} {driver_info['LastName']}",
                        'team': driver_info['TeamName']
                    })
                st.session_state.drivers = driver_list
            except Exception as e:
                st.error(f"Error loading drivers: {str(e)}")

# Main content area
if st.session_state.session:
    # Display session info
    session_info = st.session_state.session.event
    st.subheader(f"📊 {session_info['EventName']} {session_info['EventDate'].year} - {session_type}")
    
    # Driver selection
    if st.session_state.drivers:
        driver_names = [f"{d['name']} (#{d['number']})" for d in st.session_state.drivers]
        selected_driver_names = st.multiselect("Select Drivers", driver_names, default=driver_names[:2] if len(driver_names) >= 2 else driver_names)
        
        # Extract driver numbers from selected names
        selected_driver_numbers = []
        driver_lookup = {f"{d['name']} (#{d['number']})": d['number'] for d in st.session_state.drivers}
        for name in selected_driver_names:
            if name in driver_lookup:
                selected_driver_numbers.append(driver_lookup[name])
    else:
        st.warning("No drivers available for this session")
        selected_driver_numbers = []
    
    # Analysis tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Lap Times", 
        "📈 Telemetry", 
        "🗺️ Track Maps", 
        "⏱️ Sectors", 
        "📋 Driver Info"
    ])
    
    with tab1:
        st.header("Lap Time Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Generate Lap Time Comparison"):
                if selected_driver_numbers:
                    with st.spinner("Generating lap time comparison..."):
                        fig, ax = plt.subplots(figsize=(10, 6))
                        
                        for driver_number in selected_driver_numbers:
                            driver_laps = st.session_state.session.laps.pick_driver(driver_number)
                            driver_info = st.session_state.session.get_driver(driver_number)
                            driver_name = f"{driver_info['FirstName']} {driver_info['LastName']}"
                            
                            # Clean the data
                            valid_laps = driver_laps[driver_laps['LapTime'].notnull()]
                            
                            if len(valid_laps) > 0:
                                lap_numbers = valid_laps['LapNumber'].tolist()
                                lap_times_seconds = [lt.total_seconds() for lt in valid_laps['LapTime']]
                                
                                ax.plot(lap_numbers, lap_times_seconds,
                                       marker='o', linewidth=2, markersize=4,
                                       label=f"{driver_name} (#{driver_number})")
                        
                        ax.set_xlabel('Lap Number')
                        ax.set_ylabel('Lap Time (seconds)')
                        ax.set_title('Lap Time Comparison')
                        ax.legend()
                        ax.grid(True, alpha=0.3)
                        
                        st.pyplot(fig)
                else:
                    st.warning("Please select at least one driver")
        
        with col2:
            if st.button("Generate Lap Time Distribution"):
                if selected_driver_numbers:
                    with st.spinner("Generating lap time distribution..."):
                        fig, ax = plt.subplots(figsize=(10, 6))
                        
                        for driver_number in selected_driver_numbers:
                            driver_laps = st.session_state.session.laps.pick_driver(driver_number)
                            driver_info = st.session_state.session.get_driver(driver_number)
                            driver_name = f"{driver_info['FirstName']} {driver_info['LastName']}"
                            
                            # Get valid lap times
                            valid_laps = driver_laps[driver_laps['LapTime'].notnull()]
                            if len(valid_laps) > 0:
                                lap_times_seconds = [lt.total_seconds() for lt in valid_laps['LapTime']]
                                ax.hist(lap_times_seconds, alpha=0.7, label=driver_name, bins=20)
                        
                        ax.set_xlabel('Lap Time (seconds)')
                        ax.set_ylabel('Frequency')
                        ax.set_title('Lap Time Distribution')
                        ax.legend()
                        ax.grid(True, alpha=0.3)
                        
                        st.pyplot(fig)
                else:
                    st.warning("Please select at least one driver")
    
    with tab2:
        st.header("Telemetry Analysis")
        
        if len(selected_driver_numbers) >= 1:
            driver_to_analyze = st.selectbox(
                "Select Driver for Telemetry", 
                selected_driver_numbers,
                format_func=lambda x: f"Driver #{x}"
            )
            
            if st.button("Generate Telemetry Charts"):
                with st.spinner("Generating telemetry analysis..."):
                    try:
                        # Get driver info
                        driver_info = st.session_state.session.get_driver(driver_to_analyze)
                        driver_name = f"{driver_info['FirstName']} {driver_info['LastName']}"
                        
                        # Get fastest lap
                        driver_laps = st.session_state.session.laps.pick_driver(driver_to_analyze)
                        fastest_lap = driver_laps.pick_fastest()
                        
                        if not fastest_lap.empty:
                            telemetry = fastest_lap.get_telemetry()
                            
                            # Create multi-panel plot
                            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
                            fig.suptitle(f'Telemetry Analysis - {driver_name}', fontsize=14, fontweight='bold')
                            
                            # Speed
                            axes[0, 0].plot(telemetry['Distance'], telemetry['Speed'], linewidth=2, color='blue')
                            axes[0, 0].set_xlabel('Distance (m)')
                            axes[0, 0].set_ylabel('Speed (km/h)')
                            axes[0, 0].set_title('Speed Trace')
                            axes[0, 0].grid(True, alpha=0.3)
                            
                            # Throttle
                            axes[0, 1].plot(telemetry['Distance'], telemetry['Throttle'], linewidth=2, color='green')
                            axes[0, 1].set_xlabel('Distance (m)')
                            axes[0, 1].set_ylabel('Throttle (%)')
                            axes[0, 1].set_title('Throttle Usage')
                            axes[0, 1].grid(True, alpha=0.3)
                            
                            # Brake
                            axes[1, 0].plot(telemetry['Distance'], telemetry['Brake'], linewidth=2, color='red')
                            axes[1, 0].set_xlabel('Distance (m)')
                            axes[1, 0].set_ylabel('Brake (Boolean)')
                            axes[1, 0].set_title('Brake Application')
                            axes[1, 0].grid(True, alpha=0.3)
                            
                            # RPM
                            axes[1, 1].plot(telemetry['Distance'], telemetry['RPM'], linewidth=2, color='orange')
                            axes[1, 1].set_xlabel('Distance (m)')
                            axes[1, 1].set_ylabel('RPM')
                            axes[1, 1].set_title('Engine RPM')
                            axes[1, 1].grid(True, alpha=0.3)
                            
                            plt.tight_layout()
                            st.pyplot(fig)
                        else:
                            st.warning("No fastest lap data available")
                    except Exception as e:
                        st.error(f"Error generating telemetry charts: {str(e)}")
        else:
            st.info("Select drivers to analyze telemetry data")
    
    with tab3:
        st.header("Track Map Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Generate Single Driver Track Map"):
                if selected_driver_numbers:
                    driver_number = selected_driver_numbers[0]
                    with st.spinner("Generating track map..."):
                        try:
                            # Get driver info
                            driver_info = st.session_state.session.get_driver(driver_number)
                            driver_name = f"{driver_info['FirstName']} {driver_info['LastName']}"
                            
                            # Get fastest lap telemetry
                            driver_laps = st.session_state.session.laps.pick_driver(driver_number)
                            fastest_lap = driver_laps.pick_fastest()
                            
                            if not fastest_lap.empty:
                                telemetry = fastest_lap.get_telemetry()
                                
                                # Create track map
                                fig, ax = plt.subplots(figsize=(12, 12))
                                
                                # Plot track outline
                                ax.plot(telemetry['X'], telemetry['Y'], 
                                       color='black', linewidth=1, alpha=0.3, label='Track Outline')
                                
                                # Color-code by speed
                                scatter = ax.scatter(telemetry['X'], telemetry['Y'], 
                                                   c=telemetry['Speed'], 
                                                   cmap='plasma', s=8, alpha=0.8)
                                
                                # Add colorbar
                                cbar = plt.colorbar(scatter)
                                cbar.set_label('Speed (km/h)', rotation=270, labelpad=20)
                                
                                # Mark start/finish
                                ax.scatter(telemetry.iloc[0]['X'], telemetry.iloc[0]['Y'], 
                                          color='green', s=100, marker='s', label='Start/Finish')
                                
                                ax.set_xlabel('Track Position X (meters)')
                                ax.set_ylabel('Track Position Y (meters)')
                                ax.set_title(f'{driver_name} - Track Map with Speed Visualization')
                                ax.legend()
                                ax.axis('equal')
                                ax.grid(True, alpha=0.3)
                                
                                st.pyplot(fig)
                            else:
                                st.warning("No fastest lap data available")
                        except Exception as e:
                            st.error(f"Error generating track map: {str(e)}")
                else:
                    st.warning("Please select a driver")
        
        with col2:
            if len(selected_driver_numbers) >= 2:
                driver1 = selected_driver_numbers[0]
                driver2 = selected_driver_numbers[1]
                
                if st.button("Generate Driver Comparison Track Map"):
                    with st.spinner("Generating track comparison..."):
                        try:
                            # Get driver info
                            driver1_info = st.session_state.session.get_driver(driver1)
                            driver2_info = st.session_state.session.get_driver(driver2)
                            
                            driver1_name = f"{driver1_info['FirstName']} {driver1_info['LastName']}"
                            driver2_name = f"{driver2_info['FirstName']} {driver2_info['LastName']}"
                            
                            # Get fastest laps
                            driver1_laps = st.session_state.session.laps.pick_driver(driver1)
                            driver2_laps = st.session_state.session.laps.pick_driver(driver2)
                            
                            driver1_fastest = driver1_laps.pick_fastest()
                            driver2_fastest = driver2_laps.pick_fastest()
                            
                            if not driver1_fastest.empty and not driver2_fastest.empty:
                                telemetry1 = driver1_fastest.get_telemetry()
                                telemetry2 = driver2_fastest.get_telemetry()
                                
                                # Create comparison plot
                                fig, ax = plt.subplots(figsize=(12, 12))
                                
                                # Plot both drivers' tracks
                                ax.plot(telemetry1['X'], telemetry1['Y'], 
                                       color='blue', linewidth=2, alpha=0.7, label=f'{driver1_name}')
                                ax.plot(telemetry2['X'], telemetry2['Y'], 
                                       color='red', linewidth=2, alpha=0.7, label=f'{driver2_name}')
                                
                                # Mark start/finish
                                ax.scatter(telemetry1.iloc[0]['X'], telemetry1.iloc[0]['Y'], 
                                          color='green', s=150, marker='s', label='Start/Finish')
                                
                                ax.set_xlabel('Track Position X (meters)')
                                ax.set_ylabel('Track Position Y (meters)')
                                ax.set_title(f'Track Comparison: {driver1_name} vs {driver2_name}')
                                ax.legend()
                                ax.axis('equal')
                                ax.grid(True, alpha=0.3)
                                
                                st.pyplot(fig)
                            else:
                                st.warning("Could not find fastest laps for both drivers")
                        except Exception as e:
                            st.error(f"Error generating track comparison: {str(e)}")
            else:
                st.info("Select at least 2 drivers for comparison")
    
    with tab4:
        st.header("Sector Analysis")
        
        if selected_driver_numbers:
            driver_for_sectors = st.selectbox(
                "Select Driver for Sector Analysis", 
                selected_driver_numbers,
                format_func=lambda x: f"Driver #{x}"
            )
            
            if st.button("Generate Sector Analysis"):
                with st.spinner("Generating sector analysis..."):
                    try:
                        driver_info = st.session_state.session.get_driver(driver_for_sectors)
                        driver_name = f"{driver_info['FirstName']} {driver_info['LastName']}"
                        
                        # Get all laps
                        driver_laps = st.session_state.session.laps.pick_driver(driver_for_sectors)
                        
                        # Remove invalid laps
                        valid_laps = driver_laps[
                            (driver_laps['Sector1Time'].notnull()) & 
                            (driver_laps['Sector2Time'].notnull()) & 
                            (driver_laps['Sector3Time'].notnull())
                        ]
                        
                        if len(valid_laps) > 0:
                            # Convert sector times to seconds
                            sector1_times = [t.total_seconds() for t in valid_laps['Sector1Time']]
                            sector2_times = [t.total_seconds() for t in valid_laps['Sector2Time']]
                            sector3_times = [t.total_seconds() for t in valid_laps['Sector3Time']]
                            lap_numbers = valid_laps['LapNumber'].tolist()
                            
                            # Create sector time progression chart
                            fig, ax = plt.subplots(figsize=(12, 8))
                            ax.plot(lap_numbers, sector1_times, marker='o', label='Sector 1', linewidth=2)
                            ax.plot(lap_numbers, sector2_times, marker='s', label='Sector 2', linewidth=2)
                            ax.plot(lap_numbers, sector3_times, marker='^', label='Sector 3', linewidth=2)
                            
                            ax.set_xlabel('Lap Number')
                            ax.set_ylabel('Time (seconds)')
                            ax.set_title(f'Sector Time Progression - {driver_name}')
                            ax.legend()
                            ax.grid(True, alpha=0.3)
                            
                            st.pyplot(fig)
                        else:
                            st.warning("No valid laps with sector times")
                    except Exception as e:
                        st.error(f"Error generating sector analysis: {str(e)}")
        else:
            st.info("Select drivers to analyze sector times")
    
    with tab5:
        st.header("Driver Information")
        
        if st.session_state.drivers:
            df_drivers = pd.DataFrame(st.session_state.drivers)
            st.dataframe(df_drivers, use_container_width=True)
            
            # Team statistics
            st.subheader("Team Distribution")
            team_counts = df_drivers['team'].value_counts()
            st.bar_chart(team_counts)
        else:
            st.info("No driver information available")

else:
    st.info("👈 Please configure and load a session using the sidebar")

# Footer
st.markdown("---")
st.markdown("*Powered by FastF1 | F1 Telemetry Analyzer*")
