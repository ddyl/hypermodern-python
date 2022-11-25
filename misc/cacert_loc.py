"""Prints location of cacert.pem file."""
import certifi


def print_loc() -> None:
    """Function to print location of cacert.pem file."""
    print(certifi.where())
