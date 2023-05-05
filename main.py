from smwc.cli import SMWCommandLineInterface
from smwc.database import SMWCentralDatabase

from smwc.config import SQLITE_DB_FILE

app = SMWCommandLineInterface()
db = SMWCentralDatabase(SQLITE_DB_FILE)