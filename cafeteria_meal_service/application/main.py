import pandas as pd
import httpx  # Changed from requests to httpx for async support
from fastapi import FastAPI, HTTPException ,Request
import weaviate
import json
import logging
import ast
import uuid
from weaviate.classes.query import Filter
# Set up logger
logger = logging.getLogger(__name__)

WEAVIATE_URL = "http://0.0.0.0:8080"
CSV_PATH = "indian_restaurants_with_detailed_summaries.csv"
NOMIC_API_URL = "http://localhost:11434/api/embeddings"
EMBEDDING_MODEL = "nomic-embed-text"
# class_name = "DelhiRestaurant"
# class_name ="IndianRestaurant"
# class_name = "FoodItems"
# class_name = "Users"
class_name = "Foods"
no_of_nearest_neighbors = 3
app = FastAPI()

# Connect to Weaviate
client = weaviate.connect_to_local(
    host="localhost",
    port=8080,
    grpc_port=50051,
)

def infer_weaviate_type(dtype):
    if pd.api.types.is_integer_dtype(dtype):
        return "int"
    elif pd.api.types.is_float_dtype(dtype):
        return "number"
    elif pd.api.types.is_bool_dtype(dtype):
        return "boolean"
    else:
        return "text"

def create_schema():
    df = pd.read_csv(CSV_PATH)
    # Remove class if exists
    if client.schema.exists(class_name):
        client.schema.delete_class(class_name)
    # Build properties
    properties = []
    for col in df.columns:
        if col == "Summary":
            continue  # Summary will be used for vector, but still store as text
        dtype = infer_weaviate_type(df[col].dtype)
        properties.append({
            "name": col,
            "dataType": [dtype]
        })
    schema = {
        "class": class_name,
        "vectorizer": "none",  # We'll provide our own vectors
        "properties": properties
    }
    client.schema.create_class(schema)
    return {"status": "Schema created", "class": class_name, "properties": properties}
async def get_embedding(text: str) -> list[float]:
    headers = {"Content-Type": "application/json"}
    payload = {"model": EMBEDDING_MODEL, "prompt": text}
    
    try:
        async with httpx.AsyncClient(verify=False) as client:
            resp = await client.post(NOMIC_API_URL, headers=headers, json=payload)
            if resp.status_code != 200:
                logger.error(f"Ollama embedding failed: {resp.text}")
                raise ValueError(f"Embedding failed with status {resp.status_code}")
            
            data = resp.json()
            vector = data["embedding"]
            return vector
    except Exception as e:
        logger.error(f"Error getting embedding: {str(e)}")
        raise

# @app.get("/")
async def insert_data():  
    df = pd.read_csv(CSV_PATH)
    if not client.schema.exists(class_name):
        raise HTTPException(status_code=400, detail="Schema does not exist. Please create schema first.")
    for idx, row in df.iterrows():
        properties = row.to_dict()
        summary = properties.get("Summary", "")
        vector = await get_embedding(summary)  
        client.data_object.create(
            data_object=properties,
            class_name=class_name,
            vector=vector
        )
    return {"status": "Data inserted", "rows": len(df)}

async def help():
    class_schema = client.collections.get(class_name).config.get()
    print(class_schema)
@app.get("/food_details/{food_id}/")
async def get_food_details_with_id(food_id: str) -> str:
    try:
      
        food_collection = client.collections.get(class_name)
        
        food_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, food_id))
        result = food_collection.query.fetch_object_by_id(
            food_id
        )
        
        if not result:
            return f"No food item found with ID: {food_id}"

        output = "\n".join(f"{key}: {value}" for key, value in result.properties.items())
        return output
        
    except Exception as e:
        return f"Error retrieving food details: {str(e)}"
from weaviate.collections.classes.filters import Filter

@app.get("/restaurant_details/{restaurant_id}/")
async def get_restaurant_details_with_id(restaurant_id: int) -> str:
    try:
        food_collection = client.collections.get(class_name)
        
        # Create proper Weaviate filter
        restaurant_filter = Filter.by_property("restaurant_id").equal(restaurant_id)
        
        result = food_collection.query.fetch_objects(
            limit=1,
            return_properties=[
                "restaurant_id",
                "restaurant_name", 
                "restaurant_address",
                "restaurant_rating",
                "restaurant_comments"
            ],
            filters=restaurant_filter
        )
        
        if not result.objects or len(result.objects) == 0:
            return f"No restaurant found with ID: {restaurant_id}"
            
        return result.objects[0]
        
    except Exception as e:
        return f"Error retrieving restaurant details: {str(e)}"


@app.post("/restaurant_details/")
async def get_restaurants_details(restaurant_ids: list[int]) -> str:
    try:
        food_collection = client.collections.get(class_name)
        results = []
        
        for rid in restaurant_ids:
            try:
                restaurant_filter = Filter.by_property("restaurant_id").equal(rid)
                
                result = food_collection.query.fetch_objects(
                    limit=1,
                    return_properties=[
                        "restaurant_id",
                        "restaurant_name", 
                        "restaurant_address",
                        "restaurant_rating",
                        "restaurant_comments"
                    ],
                    filters=restaurant_filter
                )
                
                if result.objects:
                    restaurant = result.objects[0]
                    results.append({
                        "restaurant_id": restaurant.properties.get("restaurant_id"),
                        "restaurant_name": restaurant.properties.get("restaurant_name"),
                        "restaurant_address": restaurant.properties.get("restaurant_address"),
                        "restaurant_rating": float(restaurant.properties.get("restaurant_rating", 0)),
                        "restaurant_comments": restaurant.properties.get("restaurant_comments", "")
                    })
                else:
                    results.append({
                        "error": f"Restaurant with ID {rid} not found",
                        "restaurant_id": rid
                    })
                    
            except Exception as e:
                results.append({
                    "error": str(e),
                    "restaurant_id": rid
                })
        
        return json.dumps(results, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"System error: {str(e)}",
            "details": "Failed to process request"
        }, indent=2)
@app.post("/food_details/")
async def get_food_details_with_ids(food_ids: list[str]) -> str:
    try:
        food_collection = client.collections.get(class_name)
        results = []
        
        for food_id in food_ids:
            food_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, food_id))
            result = food_collection.query.fetch_object_by_id(food_uuid)
            
            if result:
                results.append("\n".join(f"{key}: {value}" for key, value in result.properties.items()))
        
        if not results:
            return "No food items found with the provided IDs"
            
        return "\n\n".join(results)
        
    except Exception as e:
        return f"Error retrieving food details: {str(e)}"
@app.get("/semantic_search/{text}/")
async def semantic_search(text: str):  # Made this function async
    """
    semantic search using the summary   
    """
    print(text)
    vector = await get_embedding(text)  # Added await here
    print(vector)
    connection = client.collections.get(class_name)
    filters  =  """Filter.by_property("restaurant_name").like("*delight*")"""

    filters = eval(filters)  
    response = connection.query.near_vector(
        near_vector=vector, 
        limit=no_of_nearest_neighbors,
        filters=filters
    )
    nearest_vectors = []
    for o in response.objects:
        nearest_vectors.append(o.properties)
    return nearest_vectors
@app.post("/semantic_search/")
async def semantic_search(request: Request):
    """
    Perform semantic search using the 'describe' field from raw JSON body
    to fetch vector embeddings, filtered by provided 'parameters'.
    Returns top 10 'Food_ID' values.
    """
    body: Dict[str, Any] = await request.json()
    describe = body.get("describe")
    parameters = body.get("parameters", [])
    print(type(parameters))
    vector = await get_embedding(describe)
    print(describe)
    print(parameters)
    
    connection = client.collections.get(class_name)
    
    if parameters:
        filter_str = parameters[0] 
        filters = eval(filter_str)  
        response = connection.query.near_vector(
            near_vector=vector, 
            limit=no_of_nearest_neighbors,
            filters=filters
        )
    else:
        response = connection.query.near_vector(
            near_vector=vector, 
            limit=no_of_nearest_neighbors
        )
    
    food_ids = [
        item.properties["food_id"] 
        for item in response.objects 
        if "food_id" in item.properties
    ]

    return food_ids