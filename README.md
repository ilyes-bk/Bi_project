# BI Project

This project involves web scraping data from three websites, performing Extract, Transform, Load (ETL) processes, loading the data into MongoDB, and conducting analysis using a Star Schema in PowerBI.

## Overview

- Web Scraping: Data was collected from three websites using Python, BeautifulSoup, and Requests.
- ETL Process: The collected data underwent Extract, Transform, and Load processes to prepare it for analysis.
- Database: MongoDB was used to store the processed data.
- Analysis: A Star Schema was implemented for efficient querying, and PowerBI was used for in-depth analysis and visualization.

## Technologies Used

- Python
- BeautifulSoup
- Requests
- Pandas
- NumPy
- MongoDB
- PowerBI

## Project Structure

- `web_scraping/`: Contains the Python scripts for web scraping.
- `etl/`: Includes the ETL process scripts.
- `database/`: Holds MongoDB-related files and scripts.
- `analysis/`: PowerBI files and analysis reports.

## Usage

1. **Web Scraping:**
   - Navigate to the `web_scraping/` directory.
   - Run the Python scripts to collect data from the specified websites.

2. **ETL Process:**
   - Move to the `etl/` directory.
   - Execute the ETL scripts to clean and transform the collected data.

3. **Database:**
   - Access the `database/` directory.
   - Run MongoDB scripts to load the processed data.

4. **Analysis:**
   - Open PowerBI files in the `analysis/` directory for detailed analysis and visualization.

## Dependencies

Install the required Python packages using the following command:

```bash
pip install beautifulsoup4 requests pandas numpy
