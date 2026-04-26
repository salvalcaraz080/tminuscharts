# ============================================================
# T-Minus Charts · Power BI data source
#
# Paste this script in:
#   Power BI Desktop → Get Data → Python script
#
# After running, select the tables you want to load.
# ============================================================

import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path(r"C:\Users\salca\proyectos\tminuscharts\data\tminuscharts.db")

conn = sqlite3.connect(DB_PATH)

launches  = pd.read_sql("SELECT * FROM launches",                   conn)
providers = pd.read_sql("SELECT * FROM launch_service_providers",   conn)
rockets   = pd.read_sql("SELECT * FROM rockets",                    conn)
pads      = pd.read_sql("SELECT * FROM pads",                       conn)

conn.close()
