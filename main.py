from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
import requests

app = FastAPI()

# Serve HTML page
@app.get("/")
def serve_html():
    return FileResponse("index.html")

# Fetch non-alcoholic drinks (with optional search)
@app.get("/drinks")
def get_non_alcoholic_drinks(search: str = Query(None, description="Filter drinks by name")):
    url = "https://www.thecocktaildb.com/api/json/v1/1/filter.php?a=Non_Alcoholic"
    response = requests.get(url)

    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Failed to fetch drinks from API")

    data = response.json()
    drinks_list = []

    for drink in data.get("drinks", []):
        drinks_list.append({
            "id": drink.get("idDrink"),
            "name": drink.get("strDrink"),
            "image": drink.get("strDrinkThumb")
        })

    # Apply search filter if provided
    if search:
        search_lower = search.lower()
        drinks_list = [d for d in drinks_list if search_lower in d["name"].lower()]

    return {"drinks": drinks_list}

# Fetch full details of a single drink by ID
@app.get("/drink/{drink_id}")
def get_drink_details(drink_id: str):
    url = f"https://www.thecocktaildb.com/api/json/v1/1/lookup.php?i={drink_id}"
    response = requests.get(url)

    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Failed to fetch drink details from API")

    data = response.json()
    drinks = data.get("drinks")

    if not drinks:
        raise HTTPException(status_code=404, detail="Drink not found")

    drink = drinks[0]

    # Collect ingredients dynamically
    ingredients = []
    for i in range(1, 16):  # CocktailDB supports up to 15 ingredients
        ingredient = drink.get(f"strIngredient{i}")
        measure = drink.get(f"strMeasure{i}")
        if ingredient:
            if measure:
                ingredients.append(f"{ingredient} - {measure.strip()}")
            else:
                ingredients.append(ingredient)

    return {
        "id": drink.get("idDrink"),
        "name": drink.get("strDrink"),
        "category": drink.get("strCategory"),
        "instructions": drink.get("strInstructions"),
        "ingredients": ingredients,
        "image": drink.get("strDrinkThumb"),
    }
