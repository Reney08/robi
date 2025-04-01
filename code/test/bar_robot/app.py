from flask import Flask, render_template, request, redirect, url_for, jsonify, session
# from .moveable.stepper import Stepper
from helpers.executeSequence import ExecuteSequence

import json
import glob
import os

app = Flask(__name__,
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
app.secret_key = "test123"

with open("../json/pumps.json", "r") as file:
    pumps = json.load(file)

with open("../json/positions.json") as file:
    positions = json.load(file)


# stepper_instance = Stepper()

@app.route('/')
def index():
    # List all cocktail JSON files and render the index page
    cocktail_files = glob.glob('../json/cocktails/*.json')
    cocktails = [os.path.splitext(os.path.basename(file))[0] for file in cocktail_files]
    # cocktails = db_handler.get_all_cocktails()
    print(cocktails)
    return render_template('index.html', cocktails=cocktails)


@app.route('/<selected_cocktail>')
def selected_cocktail(selected_cocktail):
    if selected_cocktail == "favicon.ico":
        return "Not a valid cocktail", 404

    # Load ingredients for the selected :
    # cocktail and render the page
    ingredients_file = f'../json/cocktails/{selected_cocktail}.json'
    if os.path.exists(ingredients_file):
        with open(ingredients_file) as f:
            ingredients = json.load(f)
            print("Loaded ingredients:", ingredients)
    else:
        ingredients = {}
        print("Ingredients file not found:", ingredients_file)

    session["ingredients"] = ingredients
    print("Session ingredients after setting:", session["ingredients"])  # Debugging

    '''
    session['ingredients'] = {
        "Vodka": 50,
        "Bananensaft": 25
    }
    '''
    return render_template('selected_cocktail.html', cocktail=selected_cocktail, ingredients=ingredients)


@app.route('/start_mixing', methods=["GET", "POST"])
def start_mixing():
    if 'ingredients' in session:
        ingredients = session['ingredients']
        print("Ingredients", ingredients)
    else:
        return "No ingredients found! Please select a cocktail first.", 400

    sequence = create_cocktail_sequence(ingredients=ingredients, pumps=pumps, positions=positions, initial_weight=0)
    execute_sequence = ExecuteSequence(sequence)
    execute_sequence.execute_sequence(sequence)
    return redirect(url_for('index'))


@app.route('/status')
def status():
    return render_template("status.html")


@app.route("/stepper/status")
def stepper_status():
    return render_template("stepper_status.html")


@app.route("/stepper/move")
def stepper_move():
    return "stepper move"


@app.route("/servo/status")
def servo_status():
    return render_template("servo_status.html")


@app.route("/servo/move")
def servo_move():
    return "servo move"


@app.route("/scale/status")
def scale_status():
    return render_template("scale_status.html")


@app.route("/scale/weight")
def scale_weight():
    return "scale weight"


@app.route('/pump')
def pump_status():
    return render_template("pump.html")


@app.route("/shutdown")
def shutdown():
    return "shut system down"

def create_cocktail_sequence(ingredients, pumps, positions, initial_weight=0):
    """
    Generate a sequence of steps to mix a cocktail based on the given ingredients.

    :param ingredients: Dict of required cocktail ingredients (liquid names and amounts in ml).
    :param pumps: Dict of pumps and their respective liquids and channels.
    :param positions: Dict of positions, their uses (servo or pump), and step coordinates.
    :param initial_weight: Initial weight of the drink container.
    :return: A list of steps to make the cocktail.
    """
    sequence = []

    # Map available pumps and positions to their liquids for lookups
    pump_lookup = {pump['liquid'].lower(): pump for pump in pumps.values()}
    position_lookup = {details['liquid'].lower(): details for details in positions.values()}

    # Track the cumulative weight dispensed
    current_weight = initial_weight

    # Process each ingredient
    for ingredient_name, amount in ingredients.items():
        ingredient = ingredient_name.lower()

        # If the ingredient is dispensed using a pump
        if ingredient in pump_lookup:
            pump = pump_lookup[ingredient]
            pwm_channel = pump['pwm_channel']

            # Calculate the target weight after dispensing
            target_weight = current_weight + amount

            # Add a pump sequence step (scale-based)
            sequence.append({
                'type': 'pump',
                'action': 'dispense',
                'details': {
                    'liquid': ingredient_name,  # Original (capitalized) name
                    'amount': amount,
                    'pwm_channel': pwm_channel,
                    'weight_target': target_weight  # Use scale to stop when target weight is reached
                }
            })

            # Update the current weight
            current_weight = target_weight

        # If the ingredient uses a servo
        elif ingredient in position_lookup:
            position = position_lookup[ingredient]

            if position['use'] == 'servo':
                # Split the amount into 25 ml portions
                num_25ml_units = amount // 25
                remainder = amount % 25

                # Add a step for each 25 ml portion
                for _ in range(num_25ml_units):
                    sequence.append({
                        'type': 'servo',
                        'action': 'dispense',
                        'details': {
                            'liquid': ingredient_name,  # Original (capitalized) name
                            'amount': 25,
                            'steps': position['steps']
                        },
                        'time_delay': 10  # 5 secs for pouring + 5 secs for refill
                    })

                # Add the remaining amount (less than 25 ml), if needed
                if remainder > 0:
                    sequence.append({
                        'type': 'servo',
                        'action': 'dispense',
                        'details': {
                            'liquid': ingredient_name,
                            'amount': remainder,
                            'steps': position['steps']
                        },
                        'time_delay': 10  # Same delay applies even for < 25 ml
                    })

        # Handle missing ingredients in both pumps and positions
        else:
            raise ValueError(f"Ingredient '{ingredient_name}' is not available in either pumps or positions.")
    make_all_lowercase(sequence)
    return sequence

def make_all_lowercase(data):
    """
        Recursively iterates over all elements in a list or dictionary
        and converts all string keys and values into lowercase.

        Args:
            data (list | dict | str): Input data, which can be a list, dictionary, or string.

        Returns:
            list | dict | str: The data with all strings converted to lowercase.
        """
    if isinstance(data, dict):  # If data is a dictionary
        return {key.lower(): make_all_lowercase(value) for key, value in data.items()}
    elif isinstance(data, list):  # If data is a list
        return [make_all_lowercase(item) for item in data]
    elif isinstance(data, str):  # If data is a string
        return data.lower()
    else:  # If data is any other type (e.g., int, float), we leave it as is
        return data


"""
def print_sequence(sequence):
    # Print the sequence in a more readable format
    print("Mixing Sequence Steps:")
    for i, step in enumerate(sequence, start=1):
        print(f"Step {i}:")
        print(f"  Type: {step['type']}")
        print(f"  Action: {step['action']}")
        print(f"  Liquid: {step['details']['liquid']} | Amount: {step['details']['amount']}ml")

        if step['type'] == 'servo':
            print(f"  Servo Steps: {step['details']['steps']}")
            print(f"  Time Delay: {step['time_delay']}s")

        elif step['type'] == 'pump':
            print(f"  PWM Channel: {step['details']['pwm_channel']}")
            print(f"  Weight Target: {step['details']['weight_target']}ml")

        print("-" * 30)  # Separator between steps

"""

if __name__ == '__main__':
    app.run(debug=True)
