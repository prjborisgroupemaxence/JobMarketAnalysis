# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 11:38:08 2019

Python script file with the functions to scrap Indeed

Can be used alone with the code in the 'Main' cell
Otherwise, get_data should be called from the main script file

@authors: Radia, David, Martial, Maxence, Philippe B
"""

import re
from datetime import date, timedelta

from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import numpy as np
from pygame import mixer #pour jouer un son dans python

import rdmmp.misc as misc

def generate_number_delay():
    """
    Return a random number following a normal distribution of mean 4 and standard deviation 0.8.
    This random number must be a time wait between every clic. The goal is to imitate a human.

    """
    mean = 4
    sigma = 0.8
    return np.random.normal(mean, sigma, 1)[0]


def play_mp3(sound):
    """
    sound :  path of the audio file
    play the sound
    """
    mixer.init()
    mixer.music.load(sound)
    mixer.music.play()

def get_soup(url):
    """
    Given the url of a page, this function returns the soup object.

    Parameters:
        url: the link to get soup object for

    Returns:
        soup: soup object
    """
    driver = webdriver.Firefox()
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    driver.close()

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
        # Since sponsored job postings are represented by "a target" instead of "a href", no need to worry here
        partial_url = link.a.get('href')
        # This is a partial url, we need to attach the prefix
        url = 'https://www.indeed.fr' + partial_url
        # Make sure this is not a sponsored posting
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
        # Since sponsored job postings are represented by "a target" instead of "a href", no need to worry here
        partial_url = link.a.get('href')
        # This is a partial url, we need to attach the prefix
        url = 'https://www.indeed.fr' + partial_url
        # Make sure this is not a sponsored posting
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
    base_url = 'https://www.indeed.fr/jobs?q={}&l={}'.format(query, location)
    soup = get_soup(base_url)
    urls = grab_job_links(soup)
    sponsored_urls = grab_sponsored_job_links(soup)

    # Get the total number of postings found
    num_found_string = soup.find(id='searchCount').getText().replace(u'\xa0', '').split()
    num_found = int(num_found_string[-2])

    # Limit number of pages to get
    max_pages = round(num_found / 10)
    if num_pages > max_pages:
        print('returning max_pages!!')
        return max_pages

    if num_pages >= 2 or num_pages == -1:
        # Start loop from page 2 since page 1 has been dealt with above
        if num_pages == -1:
            num_pages = max_pages

        for i in range(2, num_pages+1):
            num = (i-1) * 10
            base_url = 'https://www.indeed.fr/jobs?q={}&l={}&start={}'.format(query, location, num)
            try:
                soup = get_soup(base_url)
                # We always combine the results back to the list
                urls += grab_job_links(soup)
                sponsored_urls += grab_sponsored_job_links(soup)
            except:
                continue

    # Check to ensure the number of urls gotten is correct
    #assert len(urls) == num_pages * 10, "There are missing job links, check code!"

    return urls, sponsored_urls

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
        city = soupcity.find(name='div', attrs={"class":""}).getText()
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

            data = data.append({'Title':title, "City":city, "Url":url, "Posted_Date":posted_date, "Salary":salary, "Company":company, "Posting":posting}, ignore_index=True)
        except:
            continue

        percent = (i+1) / n_urls

        # Print the progress the "end" arg keeps the message in the same line
        print("Progress: {:2.0f}%".format(100*percent), end='\r')

    return data, n_urls


def get_data(query, num_pages, location):
    """
    Get all the job posting data and save in a csv file using below structure:

    Features : 'Title', 'City', 'Url', 'Salary', 'Company', 'Posting'

    The csv file name has this format: "query_location.csv"

    Parameters:
        query: Indeed query keyword such as 'Data Scientist'
        num_pages: Number of search results needed, -1 to scrap all pages
        location: location to search for

    Returns:
        df: Python dataframe including all posting data

    """
    # Convert the queried title to Indeed format
    query = '+'.join(query.lower().split())

    urls, sponsored_urls = get_urls(query, num_pages, location)

    jobs_df = pd.DataFrame(columns=["Title", "Company", "Salary", "City", "Posting", "Posted_Date", "Url"])
    sponsored_df = pd.DataFrame(columns=["Title", "Company", "Salary", "City", "Posting", "Posted_Date", "Url"])

    #  Continue only if the requested number of pages is valid (when invalid, a number is returned instead of list)
    if isinstance(urls, list):
        # Urls
        jobs_df, num_urls = get_job_ad_data(urls, jobs_df)
        print('\nAll {} non-sponsored postings have been scraped !'.format(num_urls))

        # Sponsored urls
        sponsored_df, num_sponsored_urls = get_job_ad_data(sponsored_urls, sponsored_df)
        print('\nAll {} sponsored postings have been scraped !'.format(num_sponsored_urls))

        # Remove duplicate sponsored postings
        sponsored_df.drop_duplicates(inplace=True)
        print('\n{} sponsored postings after removing duplicates !'.format(sponsored_df.shape[0]))

        # Merge les dataframes
        jobs_df = pd.concat([jobs_df, sponsored_df], ignore_index=True, sort=True)

        # Remove duplicates in the merge
        jobs_df.drop_duplicates(inplace=True)
        print('\n{} postings after removing duplicates !'.format(jobs_df.shape[0]))

        # Save the dict as csv file
        file_name = misc.CSV_DIR + '/' + query.replace('+', '_')+ '_' + location.lower() + '.csv'
        jobs_df.to_csv(file_name, encoding='utf-8', index=False)

        print('All {} postings have been scraped and saved!'.format(jobs_df.shape[0]))
    else:
        print("Maximum number of pages is only {}. Please try again!".format(urls))

    return jobs_df

#%% Main if used alone
# If script is run directly, we'll take input from the user
if __name__ == "__main__":
    QUERIES = ["data scientist", "machine learning engineer", "data engineer", "developpeur"]

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
        except:
            print("Invalid number of pages! Please try again.")

    get_data(QUERY, PAGES, location='Lyon')

    SCRAP = pd.read_csv("data_scientist_lyon.csv", encoding='utf-8', index_col=0)
