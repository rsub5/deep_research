"""
Deep Research Assistant - Hugging Face Spaces Deployment
This is the main entry point for deploying the Deep Research Assistant on Hugging Face Spaces.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path to ensure imports work
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import the main application
from deep_research_start import launch_ui

# Set environment variables for Hugging Face Spaces
os.environ.setdefault("GRADIO_SERVER_NAME", "0.0.0.0")
os.environ.setdefault("GRADIO_SERVER_PORT", "7860")

def main():
    """Main function to launch the Deep Research Assistant"""
    print("🚀 Starting Deep Research Assistant...")
    print("📝 Loading dependencies and initializing UI...")
    
    try:
        # Launch the Gradio interface
        launch_ui()
    except Exception as e:
        print(f"❌ Error starting the application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 