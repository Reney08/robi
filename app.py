import argparse
import json
import logging
import shutil
from flask import Flask
from stepper import Stepper
from servo import Servo
from scale import Scale
from cocktail import Cocktail
from routes import init_routes

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['IMAGE_FOLDER'] = 'images'

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filename='app.log', filemode='a')
logger = logging.getLogger()

# Load configuration from JSON file
try:
    with open('config.json') as config_file:
        config = json.load(config_file)
except Exception as e:
    logger.error(f"Error loading configuration: {e}")
    raise

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Control the components of the bar robot.')
parser.add_argument('--disable-servo', action='store_true', help='Disable the servo motor')
parser.add_argument('--disable-scale', action='store_true', help='Disable the scale')
args = parser.parse_args()

# Initialize components
try:
    stepper = Stepper(
        step_pin=config['step_pin'],
        direction_pin=config['direction_pin'],
        enable_pin=config['enable_pin'],
        delay_between_steps=config['us_delay'] * config['uS'],
        left_button_pin=config['left_button_pin'],
        right_button_pin=config['right_button_pin']
    )
    servo = Servo()
    scale = Scale()
    cocktail = Cocktail()
except Exception as e:
    logger.error(f"Error initializing components: {e}")
    raise

# Set initial states based on command-line arguments
if args.disable_servo:
    servo.disable()

if args.disable_scale:
    scale.disable()

def backup_data():
    """
    Back up the data to a file.
    """
    try:
        shutil.copy('data.json', 'data_backup.json')
        logger.info("Data backup successful.")
    except Exception as e:
        logger.error(f"Error backing up data: {e}")

def restore_data():
    """
    Restore the data from a backup file.
    """
    try:
        shutil.copy('data_backup.json', 'data.json')
        logger.info("Data restore successful.")
    except Exception as e:
        logger.error(f"Error restoring data: {e}")

# Restore the data when initializing
restore_data()

# Initialize routes
init_routes(app, stepper, servo, scale, cocktail)

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    finally:
        # Backup the data before shutting down
        backup_data()
