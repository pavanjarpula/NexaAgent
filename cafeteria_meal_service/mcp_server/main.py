from typing import Any, List
import random
import httpx
from mcp.server.fastmcp import FastMCP
import weaviate
from weaviate.util import generate_uuid5
from weaviate.classes.query import Filter
from datetime import datetime 
food_class_name = "Foods"
user_class  = "EmployeeWallet"
ordered_foods = "Orders"
# Initialize FastMCP server
mcp = FastMCP(name ="application_tools",
host ="0.0.0.0",
port = 8123)



application_url_exact_search ="http://0.0.0.0:8000/exact_search"
application_url_semantic_search ="http://0.0.0.0:8000/semantic_search/"
application_url_food_details = "http://0.0.0.0:8000/food_details/"
application_url_restaurant_details = "http://0.0.0.0:8000/restaurant_details/"



@mcp.tool(
   name="get_current_location",
    description="""
    Get the current location of the user
    
    Returns:
        str: Name of the location in the form of string
    """,
    annotations={
        "title": "Current Location Finder",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    }
)
async def get_current_location() -> str:
    """
     Get the current location of the user 
    
    Agruments are not needed 
    
    Return : name of the location in the form of the string 
    """
    user_location = "Sector 135 Samsung "
    return user_location



@mcp.tool(
    name="nearest_restaurant_food_data",
    description="""
    Get all the data of food and restaurants from location metioned in the argument and this data will be used to do semantic_search_for_food 
    this returns nothing because it the data is huge which stored in database can be accessed by the semantic_search_for_food tool
    
    Args:
        location (str): Current location in the form of string
    
    Returns:
        list of nearest locations 
    """ 
)

async def nearest_restaurant_food_data(location: str) -> List[str]:
    nearestlocations  =   ["Sector 136, Noida","Sector 18 Market, Noida"]
    return f"""[{nearestlocations}]  This are the list nearest address from user location address. the food and restaurant related data is saved in the data base which can be searched by using tool semantic_search_of_food """

@mcp.tool(
    name="get_food_details_with_id",
    description="""
    use this tool weather if the details about the specific food are required to answer the query if need only 
    you can get the detail of the food with its Id search in the database. This atributes we get  food :
     1)restaurant_id
     2)restaurant_name
     3)restaurant_rating
     4)food_name
     5)food_ingredients
     6)calories
     7)fat_g
     8)proteins_g
     9)price_rupee
     10)food_rating
    
    Args:
        food_id : food Id that you want to know the details example: ["12-4","3-2"]
    
    Returns:
        give the details of the food 
    """
    
)

async def get_food_details_with_id(food_ids: list[str]) -> str:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                application_url_food_details,
                json=food_ids
            )
            response.raise_for_status() 
            return response.text
            
    except httpx.HTTPStatusError as e:
        return f"HTTP error occurred: {str(e)}"
    except httpx.RequestError as e:
        return f"Request error occurred: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

@mcp.tool(
    name="get_restaurant_details_with_name",
    description="""
    use this tool only if required to answer the query if need only 
    you can get the detail of the restaurant with its name search in the database. This atributes we get  of restaurant:
     1)restaurant_id
     2)restaurant_name
     3)restaurant_rating  
     4)restaurant_comments
    Args:
       restaurant_name : metion only the name of the restaurant 
       !!!!! only the name part no suffixes like restuarant only the prfix no suffix  !!!!!!

       example : 
        user query : "get the details of the grill restaurant"
        restaurant_name : "grill"      
    
    Returns:
        give the details of the restuarant  
    """
    
)

async def get_restaurant_details_with_name(restaurant_name):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://0.0.0.0:8000/restaurant_details_with_name/",
                json={"restaurant_name": restaurant_name},
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP error occurred: {str(e)}"}
    except httpx.RequestError as e:
        return {"error": f"Request error occurred: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool(
    name="get_restaurant_details_with_id",
    description="""
    use this tool only if the details required to answer the query if need only 
    you can get the detail of the restaurant with its Id search in the database. This atributes we get  of restaurant:
     1)restaurant_id
     2)restaurant_name
     3)restaurant_rating  
     4)restaurant_comments
    Args:
        restaurant_id : Restaurant ID that you want to know the details example: ["12","3"]
    
    Returns:
        give the details of the restuarant  
    """
    
)

async def get_restaurant_details_with_id(restaurant_id : list[int]) -> str:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                application_url_restaurant_details,
                json=restaurant_id
            )
            response.raise_for_status()  
            return response.text
            
    except httpx.HTTPStatusError as e:
        return f"HTTP error occurred: {str(e)}"
    except httpx.RequestError as e:
        return f"Request error occurred: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

@mcp.tool(name="place_order_with_food_id",
description="""
You can use this tool for placing an order food with given food id 
    Args:
     user_id : this users id who is ordering the food 
     food_id : which food is ordering 
return: str

  example : 
      user query : " order me food with id F001 "
      food_id : "F001"
"""

)
async def place_order_with_food_id(user_id: int, food_id: str):
    print(user_id)
    print(food_id)
    client = None  # Initialize client variable
    
    try:
        client = weaviate.connect_to_local(
            host="localhost",
            port=8080,
            grpc_port=50051,
        )
        food_uuid = generate_uuid5(food_id)
        user_uuid = generate_uuid5(user_id)
        food_coll = client.collections.get(food_class_name)
        user_coll = client.collections.get(user_class)
        if not (food_obj := food_coll.query.fetch_object_by_id(food_uuid)):
            return "Food with this ID is not present in the database"
        
        if not (user_obj := user_coll.query.fetch_object_by_id(user_uuid)):
            return "User with this ID is not present in the database"
        
        user_wallet_bal = user_obj.properties["wallet_balance"]
        food_price = int(food_obj.properties["price_rupee"])
        
        if user_wallet_bal < food_price:
            return "User does not have enough money to order the food"

        updated_data_user = {"wallet_balance": user_wallet_bal - food_price}
        user_coll.data.update(
            uuid=user_uuid,
            properties=updated_data_user,  
        )
        
        # Add order details to Orders collection
        order_data = {
            "user_id": user_id,
            "food_id": food_id,
            "restaurant_name": food_obj.properties["restaurant_name"],
            "food_name": food_obj.properties["food_name"],
            "time": str(datetime.now()),
            "price":int(food_obj.properties["price_rupee"])
        }
        orders_coll = client.collections.get("Orders")
        orders_coll.data.insert(properties=order_data)
        
        return f"Your order has been placed and your current balance is {user_wallet_bal - food_price}"
    
    except Exception as e:
        return f"cannot able to connect the database: {str(e)}"
    
    finally:
        if client is not None:
            client.close()  # Ensure client connection is closed
@mcp.tool(
    
  name = "semantic_search_of_food",
  description = """
This tool searches for food items in the database based on a food description and optional filters.

IMPORTANT RULES:

1. Do NOT include any filters related to nearest locations. These are automatically applied and should not be repeated in either the description or filters.

2. Use filters ONLY when something cannot be expressed in the text description:
   - For exact names or strings (e.g., specific restaurant names like "McDonald's")
   - For numeric comparisons (e.g., >50, <100, =200)
   - If a condition appears in filters, do NOT repeat it in the text description
   - If no filters are needed, return an empty list: []

3. Only create filters for conditions explicitly mentioned in the user query. Do NOT invent or assume extra filters.

4. In the description, include only what is NOT already captured in filters.

5. Only on this properties you can applie filters for other things you need to decribe in the describe 

6.Filter should be represented as mentioned  in example only 

Database properties available for filters:
1) restaurant_rating : float (0-5)
2) price_rupee : integer (price in INR)
3) proteins_g : integer (protein in grams)
4)calories : integer (calories)
5)fat_g : integer  (fat in grams)
6)food_rating : float (0-5)
7)restaurant_id :int

Output:
- describe : Plain-text food description can include restaurant_name , food_name,food_ingredients, diet,flavour,course,originated_state (no numbers, and without repeating filtered content)
- parameters : List of filter string objects based on the user query  (or empty list if no filters are needed then give []) 

Returns:
List of matching food item IDs from the database.

EXAMPLE:

User query:
"suggest me spicy taste food from this Delight restaurant which has cost is less than 300 and atleast 300g protein "

Output:
describe = "spicy taste food from Delight restaurant"

parameters = (
        [ Filter.by_property("price_rupee").less_than(300) & Filter.by_property("proteins_g").greater_or_equal(300)" ]
"""

)
async def semantic_search_of_food(describe: str, parameters: list[str]) -> str:
    print(describe)
    print(parameters)
    async with httpx.AsyncClient() as client:
        response = await client.post(
            application_url_semantic_search,
            json={
                "describe": describe,
                "parameters": parameters
            }
        )
        print(describe)
        print(type(parameters))
        response.raise_for_status()  
        food_ids = response.json()
          
    return f"These are the list of food IDs as per filters and description: {food_ids}"
# Run the server
if __name__ == "__main__":
    print("Running server with SSE transport")
    mcp.run(transport="sse") 