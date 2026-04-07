# f1_telemetry_analyzer.py - Complete F1 Analysis Tool

import fastf1
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime


class F1TelemetryAnalyzer:
    def __init__(self):
        self.setup_directories()
        cache_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'f1_cache')
        fastf1.Cache.enable_cache(cache_path)
        self.session = None
        self.available_sessions = []
        # Set plot style
        try:
                plt.style.use('seaborn-v0_8')
            except Exception:
                plt.style.use('seaborn')

    def setup_directories(self):
        """Create necessary directories"""
        dirs = ['f1_cache', 'outputs']
        for directory in dirs:
            os.makedirs(directory, exist_ok=True)
                print(f"📁 Created directory: {directory}")

    def load_session(self, year, grand_prix, session_type='R'):
        """Load F1 session data"""
        try:
            print(f"📡 Loading {year} {grand_prix} {session_type} session...")
            self.session = fastf1.get_session(year, grand_prix, session_type)
            self.session.load(telemetry=True)
            print("✅ Session loaded successfully!")
            return True
        except Exception as e:
            print(f"❌ Error loading session: {e}")
            return False

    def list_drivers(self):
        """List available drivers in current session"""
        if not self.session:
            print("❌ No session loaded")
            return []

        try:
            drivers = self.session.drivers
            driver_list = []
            for driver_number in drivers:
                driver_number = int(driver_number)
                driver_info = self.session.get_driver(driver_number)
                driver_list.append({
                    'number': driver_number,
                    'name': f"{driver_info['FirstName']} {driver_info['LastName']}",
                    'team': driver_info['TeamName']
                })
            return driver_list
        except Exception as e:
            print(f"❌ Error listing drivers: {e}")
            return []

    def basic_lap_comparison(self, driver_numbers):
        """Create basic lap time comparison chart"""
        if not self.session:
            print("❌ No session loaded")
            return

        try:
            plt.figure(figsize=(12, 8))

            for driver_number in driver_numbers:
                    driver_number = int(driver_number)
                driver_laps = self.session.laps.pick_driver(driver_number)
                driver_number = int(driver_number)
                driver_info = self.session.get_driver(driver_number)
                driver_name = f"{driver_info['FirstName']} {driver_info['LastName']}"

                # Clean the data
                valid_laps = driver_laps[driver_laps['LapTime'].notnull()]

                if len(valid_laps) > 0:
                    lap_numbers = valid_laps['LapNumber'].tolist()
                    lap_times_seconds = [lt.total_seconds() for lt in valid_laps['LapTime']]

                    plt.plot(lap_numbers, lap_times_seconds,
                            marker='o', linewidth=2, markersize=4,
                            label=f"{driver_name} (#{driver_number})")

            plt.xlabel('Lap Number')
            plt.ylabel('Lap Time (seconds)')
            plt.title(f'Lap Time Comparison - {self.session.event["EventName"]} {self.session.event.year}')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()

            # Save and show
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"outputs/lap_comparison_{timestamp}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"💾 Chart saved as: {filename}")
            plt.show()

        except Exception as e:
            print(f"❌ Error in lap comparison: {e}")

    def speed_trace_comparison(self, driver_numbers):
        """Compare speed traces for fastest laps"""
        if not self.session:
            print("❌ No session loaded")
            return

        try:
            # Get driver names
            driver_names = []
            for driver_number in driver_numbers:
                    driver_number = int(driver_number)
                driver_number = int(driver_number)
                driver_info = self.session.get_driver(driver_number)
                driver_names.append(f"{driver_info['FirstName']} {driver_info['LastName']}")

            # Get fastest laps
            telemetry_data = []
            for driver_number in driver_numbers:
                    driver_number = int(driver_number)
                driver_laps = self.session.laps.pick_driver(driver_number)
                fastest_lap = driver_laps.pick_fastest()
                if not fastest_lap.empty:
                    telemetry = fastest_lap.get_telemetry()
                    telemetry_data.append(telemetry)
                else:
                    telemetry_data.append(None)

            # Create multi-panel plot
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle(f'Telemetry Comparison - {" vs ".join(driver_names)}\n{self.session.event["EventName"]} {self.session.event.year}',
                         fontsize=14, fontweight='bold')

            # Speed comparison
            for i, (driver_number, telemetry) in enumerate(
                    zip(driver_numbers, telemetry_data)):
                if telemetry is not None:
                    driver_number = int(driver_number)
                driver_info = self.session.get_driver(driver_number)
                    driver_name = f"{driver_info['FirstName']} {driver_info['LastName']}"
                    axes[0, 0].plot(telemetry['Distance'], telemetry['Speed'],
                                   label=driver_name, linewidth=2)
            axes[0, 0].set_xlabel('Distance (m)')
            axes[0, 0].set_ylabel('Speed (km/h)')
            axes[0, 0].set_title('Speed Trace Comparison')
            axes[0, 0].legend()
            axes[0, 0].grid(True, alpha=0.3)

            # Throttle comparison
            for i, (driver_number, telemetry) in enumerate(zip(driver_numbers, telemetry_data)):
                if telemetry is not None:
                    driver_number = int(driver_number)
                driver_info = self.session.get_driver(driver_number)
                    driver_name = f"{driver_info['FirstName']} {driver_info['LastName']}"
                    axes[0, 1].plot(telemetry['Distance'], telemetry['Throttle'],
                                   label=driver_name, linewidth=2)
            axes[0, 1].set_xlabel('Distance (m)')
            axes[0, 1].set_ylabel('Throttle (%)')
            axes[0, 1].set_title('Throttle Usage')
            axes[0, 1].legend()
            axes[0, 1].grid(True, alpha=0.3)

            # Brake comparison
            for i, (driver_number, telemetry) in enumerate(zip(driver_numbers, telemetry_data)):
                if telemetry is not None:
                    driver_number = int(driver_number)
                driver_info = self.session.get_driver(driver_number)
                    driver_name = f"{driver_info['FirstName']} {driver_info['LastName']}"
                    axes[1, 0].plot(telemetry['Distance'], telemetry['Brake'],
                                   label=driver_name, linewidth=2)
            axes[1, 0].set_xlabel('Distance (m)')
            axes[1, 0].set_ylabel('Brake (Boolean)')
            axes[1, 0].set_title('Brake Application')
            axes[1, 0].legend()
            axes[1, 0].grid(True, alpha=0.3)

            # RPM comparison
            for i, (driver_number, telemetry) in enumerate(zip(driver_numbers, telemetry_data)):
                if telemetry is not None:
                    driver_number = int(driver_number)
                driver_info = self.session.get_driver(driver_number)
                    driver_name = f"{driver_info['FirstName']} {driver_info['LastName']}"
                    axes[1, 1].plot(telemetry['Distance'], telemetry['RPM'],
                                   label=driver_name, linewidth=2)
            axes[1, 1].set_xlabel('Distance (m)')
            axes[1, 1].set_ylabel('RPM')
            axes[1, 1].set_title('Engine RPM')
            axes[1, 1].legend()
            axes[1, 1].grid(True, alpha=0.3)

            plt.tight_layout()

            # Save and show
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"outputs/speed_trace_comparison_{timestamp}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"💾 Speed trace comparison saved as: {filename}")
            plt.show()

        except Exception as e:
            print(f"❌ Error in speed trace comparison: {e}")

    def track_map_single_driver(self, driver_number):
        """Create track map with speed visualization for single driver"""
        if not self.session:
            print("❌ No session loaded")
            return

        try:
            # Get driver info
            driver_info = self.session.get_driver(driver_number)
            driver_name = f"{driver_info['FirstName']} {driver_info['LastName']}"

            # Get fastest lap telemetry
            driver_laps = self.session.laps.pick_driver(driver_number)
            fastest_lap = driver_laps.pick_fastest()

            if fastest_lap.empty:
                print("❌ No fastest lap found")
                return

            # Get telemetry data
            telemetry = fastest_lap.get_telemetry()

            # Create track map
            plt.figure(figsize=(12, 12))

            # Plot track outline using X,Y coordinates
            plt.plot(telemetry['X'], telemetry['Y'],
                    color='black', linewidth=1, alpha=0.3, label='Track Outline')

            # Color-code by speed
            scatter = plt.scatter(telemetry['X'], telemetry['Y'],
                               c=telemetry['Speed'],
                               cmap='plasma', s=8, alpha=0.8)

            # Add colorbar
            cbar = plt.colorbar(scatter)
            cbar.set_label('Speed (km/h)', rotation=270, labelpad=20)

            # Mark start/finish line
            plt.scatter(telemetry.iloc[0]['X'], telemetry.iloc[0]['Y'],
                       color='green', s=100, marker='s', label='Start/Finish')

            # Mark braking zones
            braking_points = telemetry[telemetry['Brake'] == True]
            if len(braking_points) > 0:
                plt.scatter(braking_points['X'], braking_points['Y'],
                           color='red', s=30, alpha=0.6, label='Braking Zones')

            plt.xlabel('Track Position X (meters)')
            plt.ylabel('Track Position Y (meters)')
            plt.title(f'{driver_name} - Track Map with Speed Visualization\n{self.session.event["EventName"]} {self.session.event.year}')
            plt.legend()
            plt.axis('equal')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()

            # Save and show
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"outputs/track_map_{driver_number}_{timestamp}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"💾 Track map saved as: {filename}")
            plt.show()

        except Exception as e:
            print(f"❌ Error creating track map: {e}")

    def track_comparison_two_drivers(self, driver1_number, driver2_number):
        """Compare two drivers' track lines"""
        if not self.session:
            print("❌ No session loaded")
            return

        try:
            # Get driver info
            driver1_number = int(driver1_number)
                driver1_info = self.session.get_driver(driver1_number)
            driver2_number = int(driver2_number)
                driver2_info = self.session.get_driver(driver2_number)

            driver1_name = f"{driver1_info['FirstName']} {driver1_info['LastName']}"
            driver2_name = f"{driver2_info['FirstName']} {driver2_info['LastName']}"

            # Get fastest laps
            driver1_laps = self.session.laps.pick_driver(driver1_number)
            driver2_laps = self.session.laps.pick_driver(driver2_number)

            driver1_fastest = driver1_laps.pick_fastest()
            driver2_fastest = driver2_laps.pick_fastest()

            if driver1_fastest.empty or driver2_fastest.empty:
                print("❌ Could not find fastest laps")
                return

            # Get telemetry data
            telemetry1 = driver1_fastest.get_telemetry()
            telemetry2 = driver2_fastest.get_telemetry()

            # Create comparison plot
            plt.figure(figsize=(15, 12))

            # Plot both drivers' tracks
            plt.plot(telemetry1['X'], telemetry1['Y'],
                    color='blue', linewidth=2, alpha=0.7, label=f'{driver1_name}')
            plt.plot(telemetry2['X'], telemetry2['Y'],
                    color='red', linewidth=2, alpha=0.7, label=f'{driver2_name}')

            # Mark start/finish
            plt.scatter(telemetry1.iloc[0]['X'], telemetry1.iloc[0]['Y'],
                       color='green', s=150, marker='s', label='Start/Finish')

            # Add speed difference visualization
            sample_interval = max(1, len(telemetry1) // 50)
            for i in range(0, len(telemetry1), sample_interval):
                if i < len(telemetry2):
                    x1, y1 = telemetry1.iloc[i]['X'], telemetry1.iloc[i]['Y']
                    x2, y2 = telemetry2.iloc[i]['X'], telemetry2.iloc[i]['Y']

                    # Draw line showing which driver is faster at this point
                    speed_diff = telemetry1.iloc[i]['Speed'] - telemetry2.iloc[i]['Speed']
                    if abs(speed_diff) > 5:
                        color = 'blue' if speed_diff > 0 else 'red'
                        alpha = min(1.0, abs(speed_diff) / 20)
                        plt.plot([x1, x2], [y1, y2], color=color, alpha=alpha, linewidth=1)

            plt.xlabel('Track Position X (meters)')
            plt.ylabel('Track Position Y (meters)')
            plt.title(f'Track Comparison: {driver1_name} vs {driver2_name}\n{self.session.event["EventName"]} {self.session.event.year}')
            plt.legend()
            plt.axis('equal')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()

            # Save and show
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"outputs/track_comparison_{driver1_number}_vs_{driver2_number}_{timestamp}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"💾 Track comparison saved as: {filename}")
            plt.show()

        except Exception as e:
            print(f"❌ Error in track comparison: {e}")

    def sector_analysis(self, driver_number):
        """Analyze sector times and performance"""
        if not self.session:
            print("❌ No session loaded")
            return

        try:
            driver_info = self.session.get_driver(driver_number)
            driver_name = f"{driver_info['FirstName']} {driver_info['LastName']}"

            # Get all laps
            driver_laps = self.session.laps.pick_driver(driver_number)

            # Remove invalid laps
            valid_laps = driver_laps[
                (driver_laps['Sector1Time'].notnull()) &
                (driver_laps['Sector2Time'].notnull()) &
                (driver_laps['Sector3Time'].notnull())
            ]

            if len(valid_laps) == 0:
                print("❌ No valid laps with sector times")
                return

            # Convert sector times to seconds
            sector1_times = [t.total_seconds() for t in valid_laps['Sector1Time']]
            sector2_times = [t.total_seconds() for t in valid_laps['Sector2Time']]
            sector3_times = [t.total_seconds() for t in valid_laps['Sector3Time']]
            lap_numbers = valid_laps['LapNumber'].tolist()

            # Create sector time progression chart
            plt.figure(figsize=(12, 8))
            plt.plot(lap_numbers, sector1_times, marker='o', label='Sector 1', linewidth=2)
            plt.plot(lap_numbers, sector2_times, marker='s', label='Sector 2', linewidth=2)
            plt.plot(lap_numbers, sector3_times, marker='^', label='Sector 3', linewidth=2)

            plt.xlabel('Lap Number')
            plt.ylabel('Time (seconds)')
            plt.title(f'Sector Time Progression - {driver_name}\n{self.session.event["EventName"]} {self.session.event.year}')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()

            # Save and show
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"outputs/sector_analysis_{driver_number}_{timestamp}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"💾 Sector analysis saved as: {filename}")
            plt.show()

        except Exception as e:
            print(f"❌ Error in sector analysis: {e}")

    def lap_time_distribution(self, driver_numbers):
        """Create lap time distribution chart"""
        if not self.session:
            print("❌ No session loaded")
            return

        try:
            plt.figure(figsize=(12, 8))

            for driver_number in driver_numbers:
                    driver_number = int(driver_number)
                driver_laps = self.session.laps.pick_driver(driver_number)
                driver_number = int(driver_number)
                driver_info = self.session.get_driver(driver_number)
                driver_name = f"{driver_info['FirstName']} {driver_info['LastName']}"

                # Get valid lap times
                valid_laps = driver_laps[driver_laps['LapTime'].notnull()]
                if len(valid_laps) > 0:
                    lap_times_seconds = [lt.total_seconds() for lt in valid_laps['LapTime']]
                    plt.hist(lap_times_seconds, alpha=0.7, label=driver_name, bins=20)

            plt.xlabel('Lap Time (seconds)')
            plt.ylabel('Frequency')
            plt.title(f'Lap Time Distribution\n{self.session.event["EventName"]} {self.session.event.year}')
            plt.legend()
            plt.grid(True, alpha=0.3)

            # Save and show
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"outputs/lap_time_distribution_{timestamp}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"💾 Lap time distribution saved as: {filename}")
            plt.show()

        except Exception as e:
            print(f"❌ Error in lap time distribution: {e}")


def main():
    analyzer = F1TelemetryAnalyzer()

    print("🏎️  F1 Telemetry Analyzer - Choose Your Analysis")
    print("=" * 60)

    # Load a session (default to 2023 Bahrain GP)
    if analyzer.load_session(2023, 'Bahrain', 'R'):
        # List available drivers
        print("\n📋 Available Drivers:")
        drivers = analyzer.list_drivers()
        for driver in drivers:
            print(f"   #{driver['number']:2} - {driver['name']:<20} ({driver['team']})")

        while True:
            print("\n🎯 Analysis Options:")
            print("1. Basic Lap Time Comparison")
            print("2. Speed Trace Comparison")
            print("3. Single Driver Track Map")
            print("4. Two Driver Track Comparison")
            print("5. Sector Time Analysis")
            print("6. Lap Time Distribution")
            print("7. List Drivers")
            print("8. Load Different Session")
            print("0. Exit")

            choice = input("\nEnter your choice (0-8): ").strip()

            if choice == '0':
                print("👋 Thanks for using F1 Telemetry Analyzer!")
                break
            elif choice == '1':
                driver_input = input("Enter driver numbers separated by commas (e.g., 1,44): ")
                driver_numbers = [num.strip() for num in driver_input.split(',')]
                analyzer.basic_lap_comparison(driver_numbers)
            elif choice == '2':
                driver_input = input("Enter driver numbers separated by commas (e.g., 1,44): ")
                driver_numbers = [num.strip() for num in driver_input.split(',')]
                analyzer.speed_trace_comparison(driver_numbers)
            elif choice == '3':
                driver_number = input("Enter driver number: ").strip()
                analyzer.track_map_single_driver(driver_number)
            elif choice == '4':
                driver1 = input("Enter first driver number: ").strip()
                driver2 = input("Enter second driver number: ").strip()
                analyzer.track_comparison_two_drivers(driver1, driver2)
            elif choice == '5':
                driver_number = input("Enter driver number: ").strip()
                analyzer.sector_analysis(driver_number)
            elif choice == '6':
                driver_input = input("Enter driver numbers separated by commas (e.g., 1,44): ")
                driver_numbers = [num.strip() for num in driver_input.split(',')]
                analyzer.lap_time_distribution(driver_numbers)
            elif choice == '7':
                drivers = analyzer.list_drivers()
                print("\n📋 Available Drivers:")
                for driver in drivers:
                    print(f"   #{driver['number']:2} - {driver['name']:<20} ({driver['team']})")
            elif choice == '8':
                year = int(input("Enter year (e.g., 2023): "))
                gp = input("Enter Grand Prix (e.g., Monaco): ")
                session_type = input("Enter session type (FP1/FP2/FP3/Q/R): ").upper()
                analyzer.load_session(year, gp, session_type)
            else:
                print("❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
