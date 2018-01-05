#!/usr/bin/env python3
# -*- coding: utf-8 -*-s
"""
Created on Mon Nov 13 16:25:02 2017

File: swissmilk_crawler.py

Author: Timo
"""

import os
import requests
from bs4 import BeautifulSoup
import re
import numpy as np
import json

# Get links for recipe subsites

os.chdir("/Users/Timo/Github/Data-Science-Projects/")

mother = "https://www.swissmilk.ch"
daughter = "/de/rezepte-kochideen/rezepte/"

def get_links(link, pattern):
    page = requests.get(link)
    soup = BeautifulSoup(page.content, 'html.parser')
    all_links = [link.get("href") for link in soup.find_all("a")]

    link_list = []
    start = 0
    for item in filter(None, all_links):
        if pattern in item:
            link_list.append(item)
        else:
            continue
        start += 1
        print("[*] link " + str(start) + " complete")
    return(link_list)
    
categories_links = []
for item in get_links(mother + daughter, "alle-rezepte"):
    categories_links.append(mother + item)
    
print(categories_links[0])
    
# Total number of recipes in subsite

def get_totalno_recipes(link):
    page = requests.get(link)    
    soup = BeautifulSoup(page.content, 'html.parser')
    total_recipes_tags = soup.find_all("h3")

    total_recipes_text = []
    for tag in total_recipes_tags:
        tag = tag.get_text()
        tag = re.sub("\s\s+", "", tag)
        total_recipes_text.append(tag)

    total_recipes_list = []
    for string in total_recipes_text:
        if any(char.isdigit() for char in string):
            total_recipes_list.append(string)
        else:
            continue
        
    total_recipes_string = total_recipes_list[0].split(" ", 1)[0]
    return(total_recipes_string)
    
totalno_recipes_list = []
for category in categories_links:
    category = get_totalno_recipes(category)
    totalno_recipes_list.append(category)
    
print(totalno_recipes_list[0])

# Get all recipe links from subsites

expand_link = "?tx_netvlmerdbclient_client%5Bpage%5D="
expand_category_links = []
for category, total in zip(categories_links, totalno_recipes_list):
    expand_category_links.append(category + expand_link + total)
    
print(expand_category_links)

recipe_link_list = []
for link in expand_category_links:
    link = get_links(link, "nr")
    recipe_link_list.append(link)
    
print(recipe_link_list[0])

# Get ingredients, ratings and macronutrients from recipe

def get_recipes(link):
    page = requests.get(link)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    def text_extractor(soup_object):
        text = []
        text = [item.get_text() for item in soup_object]
        return(text)

    def macro_cleaner(text):
        text = re.sub(r"[^\d]+", "", text)
        return(int(text))

    recipe_name = link.split("/")[6]

    rating = soup.find_all(itemprop="ratingValue")
    try:
        rating = float(text_extractor(rating)[0])
    except:
        rating = np.nan

    ingredients = soup.find_all(itemprop="ingredients")
    try:
        ingredients = text_extractor(ingredients)
    except:
        ingredients = []

    calories = soup.find_all(itemprop="calories")
    try:
        calories = int(text_extractor(calories)[0])
    except:
        calories = np.nan

    proteins = soup.find_all(itemprop="proteinContent")
    try:
        proteins = macro_cleaner(text_extractor(proteins)[0])
    except:
        proteins = np.nan

    fat = soup.find_all(itemprop="fatContent")
    try:
        fat = macro_cleaner(text_extractor(fat)[0])
    except:
        fat = np.nan

    carbs = soup.find_all(itemprop="carbohydrateContent")
    try:
        carbs = macro_cleaner(text_extractor(carbs)[0])
    except:
        carbs = np.nan
        
    ingredients_noParenthesis = []
    for string in ingredients:
        ingredients_noParenthesis.append(re.sub(r"[()]", '', string))
    
    ingredients_clean = []
    for ingredient in ingredients_noParenthesis:
        for string in ingredient.split():
            try:
                if string[0].isupper() and not string[1].isupper():
                    ingredients_clean.append(string)
                else:
                    continue
            except:
                pass
            
    recipe = {recipe_name : {
            "rating": rating,
            "ingredients" : ingredients_clean,
            "calories" : calories,
            "protein" : proteins,
            "fat" : fat,
            "carbohydrates" : carbs
            }}
    
    return(recipe)

recipes = {}
start_cat = 0
start_rec = 0
for item in recipe_link_list:
    start_cat += 1
    print("[*] Category " + str(start_cat))
    for subitem in item:
        start_rec += 1
        temp = get_recipes(mother + subitem)
        recipes.update(temp)
        print("[*] Recipe " + str(start_rec) + " complete.")
        
print("Done!")

with open('recipes.txt', 'w') as file:
     file.write(json.dumps(recipes))
