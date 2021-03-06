# -*- coding: utf-8 -*-
# pylint: disable=line-too-long
"""
Created on Tue Mar  5 11:38:08 2019

Python script file with the functions to scrap Indeed

Can be used alone with the code in the 'Main' cell
Otherwise, get_data should be called from the main script file

@authors: Radia, David, Martial, Maxence, Philippe B
"""

import re
from datetime import date, timedelta
import logging
from threading import Thread, Lock
import time

from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import numpy as np

import rdmmp.configvalues as cv

lock = Lock()
# %% Thread


class ScrapingThread(Thread):
    """
    Simple thread class, handling the scraping of num_pages pages for one (job, location) tuple
    """
    def __init__(self, job, num_pages, location, db_data):
        Thread.__init__(self)
        self.job = job
        self.num_pages = num_pages
        self.location = location
        self.db_data = db_data

    def run(self):
        # Scrap
        get_data(self.job, self.num_pages, self.location, self.db_data)

# %%
        
        
def get_soup(url):
    """
    Given the url of a page, this function returns the soup object.

    Parameters:
        url: the link to get soup object for

    Returns:
        soup: soup object
    """
    lock.acquire()
    driver = webdriver.Firefox()
    driver.get(url)
    html = driver.page_source
    
    soup = BeautifulSoup(html, 'html.parser')
    driver.close()
    time.sleep(1)
    lock.release()

    return soup


def grab_job_links(soup):
    """
    Grab all non-sponsored job posting links from a Indeed search result page using the given soup object

    Parameters:
        soup: the soup object corresponding to a search result page
                e.g. https://www.indeed.com/jobs?q=data+scientist&l=Paris&start=20

    Returns:
        urls: a python list of job posting urls

    """
    urls = []

    # Loop through all the posting links
    for link in soup.find_all('h2', {'class': 'jobtitle'}):
        partial_url = link.a.get('href')
        # This is a partial url, we need to attach the prefix
        url = 'https://www.indeed.fr' + partial_url
        # Add to the list
        urls.append(url)

    return urls


def grab_sponsored_job_links(soup):
    """
    Grab all sponsored job posting links from a Indeed search result page using the given soup object

    Parameters:
        soup: the soup object corresponding to a search result page
                e.g. https://www.indeed.com/jobs?q=data+scientist&l=Paris&start=20

    Returns:
        urls: a python list of job posting urls

    """
    sponsored_urls = []

    # Loop through all the posting links
    for link in soup.find_all('div', {'class': 'jobsearch-SerpJobCard row result clickcard'}):
        partial_url = link.a.get('href')
        # This is a partial url, we need to attach the prefix
        url = 'https://www.indeed.fr' + partial_url
        # Add to the list
        sponsored_urls.append(url)

    return sponsored_urls


def get_urls(query, num_pages, location):
    """
    Get all the job posting URLs resulted from a specific search.

    Parameters:
        query: job title to query
        num_pages: number of pages needed
        location: city to search in

    Returns:
        urls: a list of job posting URL's (when num_pages valid)
        max_pages: maximum number of pages allowed ((when num_pages invalid))
    """
    # We always need the first page
    base_url = 'https://www.indeed.fr/jobs?q={}&l={}&limit=50'.format(query, location)
    soup = get_soup(base_url)
    urls = grab_job_links(soup)
    urls += grab_sponsored_job_links(soup)

    # Get the total number of postings found
    num_found_string = soup.find(id='searchCount').getText().replace(u'\xa0', '').split()
    num_found = int(num_found_string[-2])
    
    if num_found > 1000:
        # problem, too many results, query was not specific enough
        logging.getLogger('main.scraping').warning('%d results from the simple query => plan B for accuracy', num_found)
        # Plan B, use the advanced search with more parameters to have less than 1000 results per query (salary, jobtype, age)
        num_found = 1000

    # Limit number of pages to get
    max_pages = (num_found + 49) // 50
    if num_pages > max_pages:
        num_pages = max_pages
        logging.getLogger('main.scraping').warning('Asked for too many pages, will return %d pages only', max_pages)

    if num_pages == -1:
        # We want all pages here
        num_pages = max_pages

    if num_pages >= 2:
        # Start loop from page 2 since page 1 has been dealt with above
        for i in range(2, num_pages+1):
            num = (i-1) * 50

            base_url = 'https://www.indeed.fr/jobs?q={}&l={}&limit=50&start={}'.format(query, location, num)
            try:
                soup = get_soup(base_url)
                # We always combine the results back to the list
                urls += grab_job_links(soup)
                urls += grab_sponsored_job_links(soup)
            except:
                continue

    return urls


def get_posting(url):
    """
    Get the text portion including both title and job description of the job posting from a given url
    It's the first function that call a BS and return a soup object for other information extraction

    Parameters:
        url: The job posting link

    Returns:
        title: the job title (if "data scientist" is in the title)
        posting: the job posting content
        soup : object BS
    """
    # Get the url content as BS object
    soup = get_soup(url)

    # The job title is held in the h3 tag
    try:
        title = soup.find(name='h3').getText()
    except:
        title = np.nan

    try:
        posting = soup.find(name='div', attrs={'class': "jobsearch-JobComponent-description icl-u-xs-mt--md"}).get_text().replace('\n', ' ')
    except:
        posting = np.nan

    return title, posting, soup


def get_company_name(soup):
    """
    Get the company name of the job posting from a given soup object

    Parameters:
        soup: The job posting soup object

    Returns:
        company name

    """
    try:
        company = soup.find(name='div', attrs={'class': "icl-u-lg-mr--sm icl-u-xs-mr--xs"}).get_text()
    except:
        company = np.nan

    return company


def get_salary(soup):
    """
    Get the salary of the job posting from a given soup object

    Parameters:
        url: The job posting link

    Returns:
        salary

    """
    try:
        salary = soup.find(name='span', attrs={'class': "icl-u-xs-mr--xs"}).get_text().replace(u'\xa0', '')
    except:
        salary = np.nan

    return salary

def get_location(soup):
    """
    Get the location of the job posting from a given soup object

    Parameters:
        soup: The job posting soup object

    Returns:
        location

    """
    try:
        soupcity = soup.find(name='div', attrs={'class': "jobsearch-InlineCompanyRating icl-u-xs-mt--xs jobsearch-DesktopStickyContainer-companyrating"})
        city = soupcity.find(name='div', attrs={"class": ""}).getText()
    except:
        city = np.nan

    return city


def get_posted(soup):
    """
    Get the publication date of the job posting from a given soup object

    Parameters:
        soup: The job posting soup object

    Returns:
        posted date (type DateTime)

    """
    try:
        posted = soup.find(name='div', attrs={'class': "jobsearch-JobMetadataFooter"}).getText()
        posted_since = re.findall(r"(?<=il y a) .* ", posted)[0]

        months = re.findall(r"(\d+) mois", posted_since)
        if months:
            posted_date = date.today() - timedelta(days=30*int(months[0]))
        else:
            days = re.findall(r"(\d+)\+? jour", posted_since)
            if days:
                posted_date = date.today() - timedelta(days=int(days[0]))
            else:
                posted_date = date.today()

    except:
        posted_date = np.nan

    return posted_date


def get_job_ad_data(url_lst, data):
    """
    Get the data of job postings for a list of urls from a given soup object

    Parameters:
        url_list: list of urls of job postings
        data: dataframe to append the data to

    Returns:
        n_urls
    """
    n_urls = len(url_lst)
    for i, url in enumerate(url_lst):
        try:
            title, posting, soup = get_posting(url)
            salary = get_salary(soup)
            company = get_company_name(soup)
            city = get_location(soup)
            posted_date = get_posted(soup)

            data = data.append({'Title': title, "City": city, "Url": url, "Posted_Date": posted_date, "Salary": salary, "Company": company, "Posting": posting}, ignore_index=True)
        except:
            continue

        percent = (i+1) / n_urls

        # Print the progress the "end" arg keeps the message in the same line
        print("Progress: {:2.0f}%".format(100*percent), end='\r')

    return data, n_urls


def get_data(query, num_pages, location, db_data):
    """
    Get all the job posting data and save in a csv file using below structure:

    Features : 'Title', 'City', 'Url', 'Salary', 'Company', 'Posting'

    The csv file name has this format: "query_location.csv"

    Parameters:
        query: Indeed query keyword such as 'Data Scientist'
        num_pages: Number of search results needed, -1 to scrap all pages
        location: location to search for
        db_data: data from previous scrapings

    Returns:
        df: Python dataframe including all posting data

    """
    # Convert the queried title to Indeed format
    query = '+'.join(query.lower().split())

    urls = get_urls(query, num_pages, location)
    #  Continue only if the requested number of pages is valid (when invalid, a number is returned instead of list)
    if isinstance(urls, list):    
        logging.getLogger('main.scraping').info('%s in %s: %d urls', query, location, len(urls))

        # remove duplicates in the list
        unique_urls = list(dict.fromkeys(urls))
        logging.getLogger('main.scraping').info('%s in %s: %d unique urls', query, location, len(unique_urls))

        # remove duplicated urls that are already in the database
        unique_urls[:] = [url for url in unique_urls if url not in db_data['Url']]
        logging.getLogger('main.scraping').info('%s in %s: %d unique urls not in db', query, location, len(unique_urls))

        jobs_df = pd.DataFrame(columns=["Title", "Company", "Salary", "City", "Posting", "Posted_Date", "Url"])
    
        # Urls
        jobs_df, num_urls = get_job_ad_data(unique_urls, jobs_df)
        logging.getLogger('main.scraping').info('%s in %s: %d postings have been scraped !', query, location, num_urls)
        
        jobs_df.drop_duplicates(['Title', 'Company', 'Salary', 'City', 'Posting'], inplace=True)

        # Save the dict as csv file
        file_name = cv.CFG.csv_dir.joinpath(query.replace('+', '_') + '_' + location.lower() + '.csv')
        jobs_df.to_csv(file_name, encoding='utf-8', index=False)

        logging.getLogger('main.scraping').info('%s in %s: %d postings have been  saved !', query, location, jobs_df.shape[0])
    else:
        logging.getLogger('main.scraping').warning("Maximum number of pages is only %d. Please try again!", urls)

    return jobs_df

# %%
def import_data_from_csv(folderpath, jobs, locations):
    """
    Return a dataframe with all scrap for every jobs and locations

    Parameters:
        folderpath: the location of scrap csv (ex : /scraping)
        jobs : list of all jobs (ex: jobs = ['Data Scientist', 'Developpeur', 'Business Intelligence', 'Data Analyst'] )
        locations : list of all location (ex: locations = ['Lyon', 'Paris', 'Toulouse', 'Bordeaux', 'Nantes'])

    Returns:
        alldata merged and with no duplicate rows
    """

    alldata = pd.DataFrame(columns=['Title', 'Company', 'Salary', 'City', 'Posting', 'Posted_Date', 'Url', 'Job_Category', 'Location_Category'])
    for job in jobs:
        for loc in locations:
            # version temporaire pour récupérer tous les fichiers scrapés
            # bon code en commentaire après
            for i in range(2):
                if i == 0:
                    filepath = folderpath.joinpath(job.lower().replace(' ', '_') + '_' + loc.lower() + '.csv')
                else:
                    filepath = folderpath.joinpath(job.lower().replace(' ', '_') + '_' + loc.lower() + str(i) + '.csv')

                try:
                    temp = pd.read_csv(filepath, encoding='utf-8')

                    # backward compatibility :
                    if temp.shape[1] == 8:
                        temp.drop(temp.columns[0], axis=1, inplace=True)

                    temp['Job_Category'] = job
                    temp['Location_Category'] = loc

                    alldata = alldata.append(temp, ignore_index=True)
                except FileNotFoundError:
                    logging.getLogger('main.scraping').warning('Error reading %s...', filepath)

#            filepath = folderpath.joinpath(job.lower().replace(' ', '_') + '_' + loc.lower() + '.csv')
#            try:
#                temp = pd.read_csv(filepath, encoding='utf-8')
#
#                # backward compatibility :
#                if temp.shape[1] == 8:
#                    temp.drop(temp.columns[0], axis=1, inplace=True)
#
#                alldata = alldata.append(temp, ignore_index=True)
#            except:
#                print("Error reading {}...".format(filepath))

    
    # drop les doublons sur l'ensemble des colonnes
    alldata.drop_duplicates(['Title', 'Company', 'Salary', 'City', 'Posting'], inplace=True)
    # drop les lignes où le scraping n'a pas marché (aucune info récupérée mais url ok)
    index_num = alldata[alldata['Title'].isnull() &
                        alldata['Company'].isnull() &
                        alldata['Salary'].isnull() &
                        alldata['City'].isnull() &
                        alldata['Posting'].isnull()
                       ].index
    alldata.drop(index_num, inplace=True)
    # reset de l'index
    alldata.reset_index(drop=True, inplace=True)

    return alldata

# %% Main if used alone
# If script is run directly, we'll take input from the user


if __name__ == "__main__":
    QUERIES = cv.CFG.targets

    while True:
        QUERY = input("Please enter the title to scrape data for: \n").lower()
        if QUERY in QUERIES:
            break
        else:
            print("Invalid title! Please try again.")

    while True:
        NUM_PAGES = input("Please enter the number of pages needed (integer only) or enter -1 if you want all of them: \n")
        try:
            PAGES = int(NUM_PAGES)
            break
        except ValueError:
            print("Invalid number of pages! Please try again.")

    get_data(QUERY, PAGES, location='Lyon')
    SCRAP = pd.read_csv(QUERY, encoding='utf-8', index_col=0)
