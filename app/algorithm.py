# import module
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
from textblob import TextBlob

# for graphs generation
import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO

HEADERS = ({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'})

# user define function
# Scrape the data


def getdata(url):
    r = requests.get(url, headers=HEADERS)
    return r.text


def html_code(url):

    # pass the url
    # into getdata function
    htmldata = getdata(url)
    soup = BeautifulSoup(htmldata, 'html.parser')

    # display html code
    return (soup)


# def get_names(soup):
#     # find the Html tag
#     # with find()
#     # and convert into string
#     data_str = ""
#     cus_list = []

#     for item in soup.find_all("span", class_="a-profile-name"):
#         data_str = data_str + item.get_text()
#         cus_list.append(data_str)
#         data_str = ""
#     return cus_list


def get_reviews(soup):
    # find the Html tag
    # with find()
    # and convert into string
    data_str = ""

    for item in soup.find_all("div", class_="a-expander-content reviewText review-text-content a-expander-partial-collapse-content"):
        data_str = data_str + item.get_text()

    result = data_str.split("\n")
    return (result)


def getPolarity(review):
    score = TextBlob(review).sentiment.polarity
    if score < 0:
        return 'Nagative'
    elif score == 0:
        return 'Neutral'
    else:
        return 'Positive'


def getDataFrameFromProductLink(soup):

    # html code
    # soup = html_code(url)

    # customer names
    # names = get_names(soup)

    # customer reviews
    reviews_data = get_reviews(soup)
    reviews = []
    sentiments = []

    for i in reviews_data:
        if i.strip() == "":
            pass
        else:
            reviews.append(i.strip())
            sentiments.append(getPolarity(i.strip()))

    # initialise data of lists.
    data = {'review': reviews, 'sentiment': sentiments}

    # Create n return DataFrame
    return pd.DataFrame(data)


def getProductImage(soup):

    # html code
    image = soup.find('img', {"id": "landingImage"})
    if image == None:
        return ""
    else:
        return image.get("src")


def getProductName(soup):
    name = soup.find('span', {"id": "productTitle"})
    if name == None:
        return ""
    else:
        return name.text


def getProductAbout(soup):
    ul = soup.find(
        'ul', {"class": "a-unordered-list a-vertical a-spacing-mini"})
    if ul == None:
        return ""
    else:
        return ul


def getProductBarGraphAndPieChart(df):
    plt.subplot(1, 2, 1)
    plt.bar(np.array(df['sentiment'].value_counts().index.tolist()), np.array(
        df['sentiment'].value_counts()))
    plt.title("Bar Graph")
    plt.subplot(1, 2, 2)
    plt.pie(np.array(df['sentiment'].value_counts()), radius=1.2,
            autopct='%1.0f%%', shadow=True, labels=df['sentiment'].value_counts().index.tolist())
    plt.legend(title="Sentiments :")
    plt.title("Pie Chart")

    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    buf.close()
    plt.close()
    return f"<img src='data:image/png;base64,{data}'/>"
