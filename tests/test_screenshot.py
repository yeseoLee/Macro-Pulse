import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from screenshot_utils import take_finviz_screenshot


def test_screenshot():
    print("Testing Finviz screenshot...")
    output = "test_finviz.png"
    result = take_finviz_screenshot(output)

    if result and os.path.exists(result):
        print(f"SUCCESS: Screenshot saved to {result}")
        # Clean up
        os.remove(result)
    else:
        print("FAILURE: Screenshot not taken.")


if __name__ == "__main__":
    test_screenshot()
