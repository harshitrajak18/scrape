import re
import time
import logging
import os
from django.shortcuts import render, redirect
from django.contrib import messages
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent  # Randomize User-Agent
import google.generativeai as genai
import uuid
from django.conf import settings


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure API key for generative AI
os.environ['API_KEY'] = "AIzaSyDKpl6T91i4rbKSqHhut934Z7jzuxmocQg"  # Make sure to keep your API key secure
genai.configure(api_key=os.environ.get("API_KEY"))

# Global variable to hold AI response
ai_response = ""

def setup_driver():
    """Set up the Edge WebDriver with options."""
    edge_driver_path =os.path.join(settings.BASE_DIR,"msedgedriver")
    options = Options()
    options.use_chromium = True
    options.add_argument("--headless")  # Run browser without UI
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")

    # Randomize User-Agent to avoid detection
    ua = UserAgent()
    user_agent = ua.random
    options.add_argument(f"user-agent={user_agent}")

    service = Service(edge_driver_path)
    return webdriver.Edge(service=service, options=options)

def scrape_site(request):
    """View function to handle web scraping and AI generation."""
    global ai_response  # Declare ai_response as global

    if request.method == 'POST':
        url = request.POST.get('url')
        prompt = request.POST.get('prompt')

        try:
            # Initialize Selenium WebDriver
            with setup_driver() as driver:
                logger.info(f"Navigating to the URL: {url}")
                driver.get(url)

                # Wait for the <body> tag to load
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                logger.info("Page loaded successfully.")

                # Extract text from the body tag
                body = driver.find_element(By.TAG_NAME, "body")
                whole_text = body.text

                # Generate content using the AI model
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(f"{whole_text} {prompt}")

                # Log and inspect raw AI response
                logger.info(f"Raw AI Response: {response.text}")  # Helpful for debugging

                # Save the AI response to the global variable
                ai_response = response.text

                # Render template with extracted data as 'response'
                return render(request, "home.html", {'response': ai_response})

        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect("home")

    # Render home page for GET requests
    return render(request, "home.html")

def download(request):
    global ai_response  # Access the global AI response
    if ai_response:
        with open("file.txt", "w") as f:
            f.write(ai_response)  # Use write instead of writelines
        messages.success(request, "File downloaded successfully!")
        return redirect("home")  # Redirect to home after download
    else:
        messages.error(request, "No response to download.")
        return redirect("home")
