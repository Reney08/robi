function toggleMenu() {
    const menuContent = document.getElementById('menuContent');
    menuContent.style.display = menuContent.style.display === 'block' ? 'none' : 'block';
}

function showPage(pageId) {
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => {
        page.classList.remove('active');
    });
    document.getElementById(pageId).classList.add('active');
    
    // Close the menu
    document.getElementById('menuContent').style.display = 'none';

    // Enable/disable CSS files
    document.getElementById('stepperCSS').disabled = pageId !== 'stepper';
    document.getElementById('servoCSS').disabled = pageId !== 'servo';
    document.getElementById('scaleCSS').disabled = pageId !== 'scale';
}

function setProgress(percentage) {
    document.getElementById('progress-bar').style.width = percentage + '%';
}

// Example data for stepper motor
let currentPosition = 50; // Current position (0-100)
let isMoving = true; // Is the motor currently moving
let direction = "Forward"; // Direction of movement
let isEnabled = true; // Is the motor enabled

// Update the UI for stepper motor
document.getElementById('currentPos').querySelector('.progress').style.width = currentPosition + '%';
document.getElementById('movingStatus').textContent = isMoving ? 'Yes' : 'No';
document.getElementById('direction').textContent = direction;
document.getElementById('enabledStatus').textContent = isEnabled ? 'Yes' : 'No';

// Example data for servo motor
let servoPosition = "Up"; // Current position (Up or Down)
let isServoMoving = false; // Is the servo currently moving
let isServoEnabled = true; // Is the servo enabled

// Update the UI for servo motor
document.getElementById('servoPosition').textContent = servoPosition;
document.getElementById('servoMoving').textContent = isServoMoving ? 'Yes' : 'No';
document.getElementById('servoEnabled').textContent = isServoEnabled ? 'Yes' : 'No';

// Example data for scale
let currentWeight = 1.5; // Current weight in KG
let isActive = true; // Is the scale active
let isScaleEnabled = true; // Is the scale enabled

// Update the UI for scale
let weightPercentage = (currentWeight / 2) * 100;
document.getElementById('currentWeight').querySelector('.progress').style.width = weightPercentage + '%';
document.getElementById('weightValue').textContent = currentWeight + ' KG';
document.getElementById('isActive').textContent = isActive ? 'Yes' : 'No';
document.getElementById('isEnabled').textContent = isScaleEnabled ? 'Yes' : 'No';

// Example data for initialization status and current task
let stepperInit = true; // Is the stepper initialized
let servoInit = true; // Is the servo initialized
let scaleInit = true; // Is the scale initialized
let currentTask = "Waiting for user to select and start the cocktail mixing"; // Current task

// Update the UI for initialization status and current task
document.getElementById('stepperInit').textContent = stepperInit ? 'Yes' : 'No';
document.getElementById('servoInit').textContent = servoInit ? 'Yes' : 'No';
document.getElementById('scaleInit').textContent = scaleInit ? 'Yes' : 'No';
document.getElementById('currentTask').textContent = currentTask;
