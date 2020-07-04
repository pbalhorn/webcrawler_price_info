# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 09:21:47 2019

@author: BALHORN
"""

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import pandas as pd
import numpy as np

def prices(page,WebUrl):
    if(page>0):
        subcategory_prices = []
        url = WebUrl
        code = requests.get(url)
        plain = code.text
        s = BeautifulSoup(plain, "html.parser")
        for link in s.findAll('span', {'class':'price'}):
            price = float(link.get_text().replace('€','').replace('.','').replace(',','.'))
            subcategory_prices += [price]
    return subcategory_prices

def categorys(page,WebUrl):
    if(page>0):
        category = []
        url = WebUrl
        s = requests.Session()
        s.max_redirects = 50
        code = s.get(url, headers={'user-agent': 'My app'})
        plain = code.text
        s = BeautifulSoup(plain, "html.parser")
        #print(s)
        for sc in s.findAll('script'):
            txt = sc.get_text()
            if 'PartFinder.options.categories' in txt:
                for u in txt.split('='):
                    if 'url' in u:
                        for url in u.split(','):
                            if 'url' in url and 'golf-4' in url:
                                raw_s = r'{}'.format(url.replace('\/','/')[7:-1])
                                category += [raw_s]
    return category

# %% Kategorien einlesen

categ_dict = {}

categ = categorys(1, r'https://www.volkswagen-classic-parts.de/ersatzteile/golf/golf-4.html')
new_categ = [s for s in categ if s != r'https://www.volkswagen-classic-parts.de/ersatzteile/golf/golf-4.html']
for cat in new_categ:
    #print(cat)
    sub_categ = categorys(1, cat + r'/')
    new_sub_categ = [s for s in sub_categ if s not in categ]
    #print(new_sub_categ)
    categ_dict[cat] = new_sub_categ

# %% Werte für jede Kategori einlesen

Preise = pd.DataFrame(index=['min','max','mean'])

for categ in categ_dict.keys():
    cat_name = categ.split(r'/')[-1].replace('.html','')
    for subcateg in categ_dict[categ]:
        subcat_name = subcateg.split(r'/')[-1].replace('.html','')
        price = prices(1, subcateg)
        print((cat_name,subcat_name), price)
        if len (price)==0:
            pass
        else:
            Preise[(cat_name,subcat_name)] = [np.min(price),np.max(price),np.median(price)]


# %% test

subc = r'https://www.volkswagen-classic-parts.de/ersatzteile/golf/golf-4/motor/nockenwellen.html'

price = prices(1, subc)
print(price)

# %% Preise sortiren

neue_Preise = Preise.T
neue_Preise.sort_values(by=['mean'],inplace=True,ascending=False)
print(neue_Preise.head(35))
