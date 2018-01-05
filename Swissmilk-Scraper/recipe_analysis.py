#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 18 16:50:15 2017

recipe_analysis.py

Author: Timo
"""

# Read File

import os
import json
from collections import Counter
import pandas as pd

os.chdir("/Users/Timo/GitHub/Data-Science-Projects/")

recipes = json.load(open("recipes.txt"))

# Count ingredient occurrences in corpus

recipe_keys = []
for key in recipes.keys():
    recipe_keys.append(key)
    
recipes_ingredients = []
for recipe in recipes:
    recipes_ingredients.append(recipes[recipe]["ingredients"])
    
recipes_ingredients_flat = [item for sublist in recipes_ingredients for item in sublist]

ingredients_count = Counter(recipes_ingredients_flat)

ingredients_df = pd.DataFrame.from_dict(ingredients_count, orient="index")
ingredients_df = ingredients_df.reset_index()
ingredients_df.columns = ["Ingredient", "Count"]

ingredients_df["Ingredient"].replace(regex=True,inplace=True,to_replace=r'[,:*]',value=r'')
ingredients_df = ingredients_df.groupby([ingredients_df['Ingredient']]).sum().reset_index()
ingredients_df = ingredients_df.sort_values("Count", ascending = False)
ingredients_df["Cum_Perc"] = 100 * ingredients_df.Count.cumsum() / ingredients_df.Count.sum()

ingredients_subset = ingredients_df[ingredients_df["Cum_Perc"] < 80]
print(ingredients_subset.head())
print(ingredients_subset.tail())

# Non-vegan list

non_vegan = ["Butter", "Bratcrème", "Bratbutter", "Milch", "Rahm", "Eier", 
             "Eigelb", "Ei", "Vollrahm", "Sbrinz", "Fleischbouillon",
             "Gruyère", "Honig", "Halbrahm", "Saucenhalbrahm", "Jogurt",
             "Pouletbrüstchen", "Mascarpone", "Gelatine", "Halbfettquark",
             "Quark", "Frischkäse", "Mozzarella", "Rahmquark", 
             "Fertig-Butterkuchenteig", "Ricotta", "Bergkäse", "Magerquark",
             "Rindfleisch", "Hühnerbouillon", "Rohschinken", "Butterflocken",
             "Schinken", "Butterblätterteig", "Raclettekäse", "Tilsiter",
             "Milchwasser", "Metzger", "Hüttenkäse", "Kalbsfond", "Doppelrahm",
             "Emmentaler", "Feta-Art", "Kalbsbrät"]

dairy = ["Butter", "Bratcrème", "Bratbutter", "Milch", "Rahm", "Vollrahm", 
         "Sbrinz", "Gruyère", "Halbrahm", "Saucenhalbrahm", "Jogurt",
         "Mascarpone", "Halbfettquark", "Quark", "Frischkäse", "Mozzarella", 
         "Rahmquark", "Fertig-Butterkuchenteig", "Ricotta", "Bergkäse", 
         "Magerquark", "Butterflocken", "Butterblätterteig", "Raclettekäse", 
         "Tilsiter", "Milchwasser", "Hüttenkäse", "Doppelrahm",
         "Emmentaler", "Feta-Art",]

# Create global dataframe

df_recipes = pd.DataFrame.from_dict(recipes, orient="index")
print(df_recipes.head())
print(df_recipes.tail())

# Vegan & dairy test

def ingredient_tester(list_, type_, reverse = False):
    
    counter = 0
    opposite_counter = 0
    for row in df_recipes["ingredients"]:
        if set.intersection(set(list_), set(row)) == {}:
            counter += 1
        else:
            opposite_counter += 1
    
    if reverse:
        return(type_+": " + str(opposite_counter), "non-"+type_+": " + str(counter))
    else:
        return(type_+": " + str(counter), "non-"+type_+": " + str(opposite_counter)) 
    
vegan_test = ingredient_tester(non_vegan, "vegan")
print(vegan_test)

dairy_test = ingredient_tester(dairy, "dairy", reverse = True)
print(dairy_test)