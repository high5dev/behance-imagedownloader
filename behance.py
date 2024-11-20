import os
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import tkinter as tk
from tkinter import filedialog, messagebox

# Function to download images from project links
def download_images(main_url, save_folder):
    # Set up Selenium WebDriver options
    options = Options()
    options.add_argument("--headless")  # Run in headless mode (no browser window)
    service = Service(ChromeDriverManager().install())

    # Start WebDriver
    driver = webdriver.Chrome(service=service)
    driver.get(main_url)

    # Scroll to ensure all content is loaded
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(20)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Parse the main page to find project links
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    project_link_tags = soup.find_all('a', class_='ProjectCoverNeue-coverLink-U39')
    project_links = ['https://www.behance.net' + tag['href'] for tag in project_link_tags if 'href' in tag.attrs]
    
    driver.quit()

    # Iterate over each project link and extract images
    count = 0
    for link in project_links:
        driver = webdriver.Chrome(service=service)
        driver.get(link)
        time.sleep(2)

        # Parse the project page source
        project_soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()

        # Extract image URLs from the project page
        image_divs = project_soup.find_all('div', class_='project-module-image-inner-wrap js-module-container-reference Image-container-z3a')
        for div in image_divs:
            img_tag = div.find('img')
            if img_tag and 'src' in img_tag.attrs:
                img_url = img_tag['src']
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url

                # Create a unique image name
                img_name = f"image_{count}.jpg"
                try:
                    img_response = requests.get(img_url)
                    img_response.raise_for_status()

                    with open(os.path.join(save_folder, img_name), 'wb') as img_file:
                        img_file.write(img_response.content)
                    count += 1
                except requests.exceptions.RequestException as e:
                    print(f"Failed to download {img_url}: {e}")

    if count > 0:
        messagebox.showinfo("Success", f"Downloaded {count} images to {save_folder}")
    else:
        messagebox.showinfo("Info", "No images found to download.")

# Function to choose save directory and start download
def choose_directory_and_download():
    url = url_entry.get()
    if not url:
        messagebox.showwarning("Input Error", "Please enter a URL.")
        return
    
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        download_images(url, folder_selected)

# Set up the Tkinter GUI
root = tk.Tk()
root.title("Image Downloader")

frame = tk.Frame(root)
frame.pack(pady=10)

url_label = tk.Label(frame, text="Enter URL:")
url_label.pack(side="left")
url_entry = tk.Entry(frame, width=50)
url_entry.pack(side="left", padx=5)

download_button = tk.Button(root, text="Choose Directory and Download", command=choose_directory_and_download)
download_button.pack(pady=10)

root.mainloop()
