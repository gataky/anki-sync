import random

def generate_guid(length: int = 10) -> str:
    """
    Generates a random string of a specified length using hexadecimal characters
    from a UUID.
    """
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!#$%&*+,-.:;=?@^_|~"
    return "".join(random.choices(alphabet, k=length))
