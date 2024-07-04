# Scraping

## About this project

A scraper for one of Sweden's premier legal to scrape PDF URLs and metadata from this website https://www.domstol.se/hogsta-domstolen/avgoranden/.

## Prerequisites

- Python 3.11
- ChromeDriver for selenium
- Required Python packages (requirements.txt)

## Installation

- Create a .env file with the structure of the **.env.template**
- Run **make venv** to install python packages
- Run **python run_dev.py** to run the script

## Usage

- The scraper navigates to the specified URL, applies filters, and extracts PDF URLs from the page source.
- It then fetches metadata for each PDF and saves it to metadata.json and metadata.csv.
- Latest 10 PDFs are downloaded to the specified directory.
