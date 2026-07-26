from pathlib import Path
from datetime import datetime

ENERGYPLUS_DIR = Path(r"C:\EnergyPlusV26-1-0")

EXAMPLE_FILE = ENERGYPLUS_DIR / "ExampleFiles" / "SmallOffice_CentralDOAS.idf"

WEATHER_FILE = (
    ENERGYPLUS_DIR
    / "WeatherData"
    / "USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw"
)

# Timestamped output dir prevents SQLite lock conflicts on re-run
_run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_DIR = Path(f"./simulations/output_{_run_timestamp}")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PLANNING_INTERVAL = 10