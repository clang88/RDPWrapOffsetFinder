import os
import subprocess
import logging
from logging.handlers import TimedRotatingFileHandler
import datetime

LOG_FILENAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_offset_finder.log")
INI_PATH = r"C:\\Program Files\\RDP Wrapper\\rdpwrap.ini"

def setup_logger():
    logger = logging.getLogger("OffsetFinderLogger")
    logger.setLevel(logging.INFO)
    # TimedRotatingFileHandler: rotates at midnight, keeps 31 days
    handler = TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=31, encoding="utf-8")
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    logger.handlers = []  # Remove any existing handlers
    logger.addHandler(handler)
    return logger

def main():
    logger = setup_logger()
    offset_finder_path = os.path.abspath("64bit\\RDPWrapOffsetFinder_nosymbol.exe")
    try:
        result = subprocess.run(offset_finder_path, capture_output=True, text=True, check=False)
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        if result.returncode != 0 or stderr:
            logger.error(f"Offset finder error: {stderr if stderr else 'Unknown error'}")
            print("Error running offset finder. See log for details.")
            return
        # Read ini file
        try:
            with open(INI_PATH, "r", encoding="utf-8") as rdp_wrapper_ini:
                contents = rdp_wrapper_ini.read()
        except FileNotFoundError:
            logger.error(f"INI file not found: {INI_PATH}")
            print("rdpwrap.ini not found. See log for details.")
            return
        if stdout in contents:
            logger.info("Current offset already in ini")
            print("Current offset already in ini.")
        else:
            with open(INI_PATH, "a", encoding="utf-8") as rdp_wrapper_ini:
                rdp_wrapper_ini.write("\n" + stdout + "\n")
            logger.info("Appended current offset to the ini:\n%s", stdout)
            print(f"Appended current offset to the ini.\n{stdout}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print("Unexpected error occurred. See log for details.")

if __name__ == "__main__":
    main()

