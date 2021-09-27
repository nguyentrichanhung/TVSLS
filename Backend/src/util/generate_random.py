import string
import random

def generate_random(random_length):

    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for _ in range(random_length))