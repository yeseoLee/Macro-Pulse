import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from screenshot_utils import take_finviz_screenshot, take_kospi_screenshot
import argparse


def test_screenshot(target="finviz"):
    print(f"Testing {target} screenshot...")
    
    if target == "finviz":
        output = "test_finviz.png"
        result = take_finviz_screenshot(output)
    elif target == "kospi":
        output = "test_kospi.png"
        result = take_kospi_screenshot(output)
    else:
        print(f"Unknown target: {target}")
        return

    if result and os.path.exists(result):
        print(f"SUCCESS: Screenshot saved to {result}")
        # Clean up if not specified to keep
        if not os.environ.get("KEEP_TEST_ARTIFACTS"):
            os.remove(result)
        else:
            print("KEEP_TEST_ARTIFACTS set. File preserved.")
    else:
        print("FAILURE: Screenshot not taken.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default="finviz", choices=["finviz", "kospi"], help="Target website to screenshot")
    args = parser.parse_args()
    
    test_screenshot(target=args.target)
