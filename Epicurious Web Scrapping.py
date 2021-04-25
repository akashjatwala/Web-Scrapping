# This project will scrape Epicurious to find dishes as per the user search ingredient
# The result will be in the form of a Dictionary, and the results will be dish name, description, link, ingredients, and preperation


import requests
from bs4 import BeautifulSoup

def get_recipes(keywords):
    recipe_list = []
    url = "http://www.epicurious.com/search/" + keywords
    response = requests.get(url)
    if not response.status_code == 200:
        return None
    try:
        results_page = BeautifulSoup(response.content,'lxml')
        recipes = results_page.find_all('article',class_="recipe-content-card")
        for recipe in recipes:
            recipe_link = "http://www.epicurious.com" + recipe.find('a').get('href')
            recipe_name = recipe.find('a').get_text()
            try:
                recipe_description = recipe.find('p',class_='dek').get_text()
            except:
                recipe_description = ''
            recipe_list.append((recipe_name,recipe_link,recipe_description))
        return recipe_list
    except:
        return None
        
def get_recipe_info(recipe):
    recipe_link=recipe[1]
    recipe_dict = dict()
    try:
        response = requests.get(recipe_link)
        if not response.status_code == 200:
            return recipe_dict
        result_page = BeautifulSoup(response.content,'lxml')
        ingredient_list = list()
        prep_steps_list = list()
        for ingredient in result_page.find_all('li',class_='ingredient'):
            ingredient_list.append(ingredient.get_text())
        for prep_step in result_page.find_all('li',class_='preparation-step'):
            prep_steps_list.append(prep_step.get_text().strip())
        recipe_dict['Name'] = recipe[0]
        recipe_dict['Descripion'] = recipe[2]
        recipe_dict['Link']=recipe[1]
        recipe_dict['Ingredients'] = ingredient_list
        recipe_dict['Preparation'] = prep_steps_list   
        recipe_dict_order=["Name","Description","Link","Ingredients","Preperation"]   
        reordered_recipe_dict = {k: recipe_dict[k] for k in recipe_dict_order}  
        return reordered_recipe_dict
    except:
        return recipe_dict
        
def get_all_recipes(keywords):
    results = list()
    recipe_dict={}
    all_recipes = get_recipes(keywords)
    for recipe in all_recipes:
        recipe_dict = get_recipe_info(recipe)
        results.append(recipe_dict)
    return(results)
    
def main():
    keywords = input("Please enter the things you want to see in a recipe: ")
    recipes_list = get_all_recipes(keywords)
    print(recipes_list)
    
main()
