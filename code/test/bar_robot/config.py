import os

class Config:
    # Set the secret key to a value from the environment variable 'SECRET_KEY'
    # or use a default value if the environment variable is not set
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    
    # Enable or disable debug mode
    DEBUG = True
