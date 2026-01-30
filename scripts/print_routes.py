import sys
import os
import asyncio

# Add the backend directory to sys.path so we can import app
sys.path.append(os.path.join(os.getcwd(), ".."))

# Use the absolute path to ensure we import the correct app
sys.path.append(r"c:\Users\ghild\OneDrive\Desktop\one-month\backend")

from app.main import app
from fastapi.routing import APIRoute


def print_routes():
    output = []
    output.append("Listing USER routes:")
    found = False
    for route in app.routes:
        if isinstance(route, APIRoute):
            if "user" in route.path.lower():
                output.append(
                    f"Path: {route.path} | Methods: {route.methods} | Name: {route.name}"
                )
                found = True

    if not found:
        output.append("No user routes found!")

    with open("routes.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output))
    print("Routes written to routes.txt")


if __name__ == "__main__":
    print_routes()
