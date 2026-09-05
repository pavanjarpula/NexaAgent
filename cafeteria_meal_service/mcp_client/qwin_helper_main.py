import requests
from fastapi import FastAPI, HTTPException,Request
import json
import asyncio
import subprocess
from mcp import ClientSession
from mcp.client.sse import sse_client
import weaviate
from weaviate.util import generate_uuid5
from weaviate.classes.query import Filter
from datetime import datetime 

food_class_name = "Foods"
user_class  = "EmployeeWallet"
ordered_foods = "Orders"

mcp_server_url = "http://127.0.0.1:8123/sse"
quin_url = "http://localhost:11434/v1/chat/completions"
mcp = FastAPI()
mcp.state.user_history =  []

async def initialize_mcp_session():
    async with sse_client(mcp_server_url) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools_result = await session.list_tools()
            tool_list = []
            for tool in tools_result.tools:
                properties = {}
                if hasattr(tool, 'inputSchema') and tool.inputSchema and 'properties' in tool.inputSchema:
                    properties = {
                        prop_name: {
                            "type": prop_info.get('type', 'string'),
                            "description": ""
                        }
                        for prop_name, prop_info in tool.inputSchema['properties'].items()
                    }
                
                required = []
                if hasattr(tool, 'inputSchema') and tool.inputSchema and 'required' in tool.inputSchema:
                    required = [
                        param for param in tool.inputSchema['required'] 
                        if param in properties
                    ]
                
                tool_description = {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description.strip() if hasattr(tool, 'description') else "",
                        "parameters": {
                            "type": "object",
                            "properties": properties,
                            **({"required": required} if required else {})
                        }
                    }
                }
                tool_list.append(tool_description)
            return tool_list

async def call_tool(tool: str, argu) -> str:
    try:  
        if not isinstance(argu, dict):
            return "Error: Arguments must be provided as a dictionary"
            
        async with sse_client(mcp_server_url) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize() 
                try:
                    result = await session.call_tool(tool, arguments=argu)
                except Exception as e:     
                    return  "either the tool name is not present else the arguments of the tool are not in correct form of json of arguments of the function"
                output = []
                for re in result.content:
                    output.append(re.text)
                return str(output)             
    except Exception as e:
        return f"Error: The input arguments form or the function name you want to use is not correct - {str(e)}"

async def final_prompt(history, user_query):
    prompt = f"""  you are an meal planner Assistant should answer only user queries related to  food , restaurants,user location not any other user queries should be responded 
       provide a clear, helpful answer to the user's question.

        User Question: {user_query}
        information to answer the user Question : {history}

        Provide a natural language response that directly answers the user's question based on the information to answer the user Question  provided in the Json of below attributes . Be concise and helpful:

        FinalResponse: explain why this food items are related to user query 
        Actioninput : if about some food is discused int the FinalAnswer then mention those ids only  in the list or else give empty list  example : ["1-3","2-3"] or []

        !!!!! Mandatorily  maintain this for Response  !!!!!
        you give  FinalResponse and Actioninput as outputs 
        Respond using JSON of FinalResponse and Actioninput
        !!!!!!!!!!!!!!
         
         !!!!! Mandatorily follow this !!!!!!
        check if the food ids completely satisfies all the points in the user query or not . if not then remove those id from list 
        !!!!!

        !!!!!!! If the food items is completely not related to the user query then remove it from the list of Acitoninput and finalResponse  even you can give an empty list also 
        example : 
        User Question: suggest me spicy taste food with paneer from this corner restaurant which has cost is less than 100
        Reasoning : "Here are some spicy taste food options with paneer from nearby restaurants that cost less than 100 rupees: 1. Pani puri (pri…rupees) from Haldiram's, 2. Koshimbir (price: 80 rupees) from Maharaja Bhog, 3. Papadum (price: 40 rupees) from Keraleeyam."
        FinalResponse : there are no food items with paneer less than 100 
        Actioninput : []
        !!!!!!!!!!

        example : -
        user query : "give me details of the restaurant with id 1" 
        FinalResponse :  "the restaurant details of id 1 is Hyderabadi Delight is a well-rated restaurant (3.4/5) located at H.No. 03, Iyengar Circle, Katni, Delhi NCR. Known as the 'best restaurant in town,' it offers a delightful dining experience"
        Actioninput : []

        """
    
    payload = {
        "messages": [{"role": "user", "content": prompt}]
    }

    json_payload = json.dumps(payload)
    curl_command = [
            'curl',
            '-X', 'POST',
            '--header', 'Content-Type: application/json',
            '--data', json_payload,
            quin_url  
        ]
    
    try:
        result = subprocess.run(curl_command, 
                                capture_output=True, 
                                text=True, 
                                check=True)
        output = result.stdout
        response = json.loads(output)
        print(response)
        content = json.loads(response['choices'][0]['message']['content'])
        print("\n")
        print("\n")
        print(content)
        return content
    except subprocess.CalledProcessError as e:
        print(f"Error executing curl command: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
async def text_response(json_response):
    print("hellooo")
    try:
        if "error" in json_response:
            return ["error", None]
            
        content = json.loads(json_response)["content"]
        
        if not isinstance(content, dict) or "Actioninput" not in content or "FinalResponse" not in content:
            return [content.get("FinalResponse", "Invalid response format"), None]

        food_details = []
        button_infos = []
        food_info = content["FinalResponse"]+"\n"
        print("come one ")
        print(food_info)
        
        for food_id in content["Actioninput"]:
            weaviate_client = weaviate.connect_to_local(
                host="localhost",
                port=8080,
                grpc_port=50051
            )
            try:
                food_collection = weaviate_client.collections.get("Foods")
                food_uuid = generate_uuid5(food_id)
                food_obj = food_collection.query.fetch_object_by_id(food_uuid)
                
                if food_obj is None:
                    continue
                    
                food_in = "\n\n".join([
                    f"\n**Food Name: {food_obj.properties['food_name']}**",
                    f"- Restaurant: {food_obj.properties['restaurant_name']}",
                    f"- Rating: {food_obj.properties['food_rating']}",
                    f"- Price: ₹{food_obj.properties['price_rupee']}",
                    f"- ID: {food_obj.properties['food_id']}",
                    f"- Calories: {food_obj.properties['calories']}",
                    f"- Proteins: {food_obj.properties['proteins_g']}g",
                    f"- Ingredients: {food_obj.properties['food_ingredients']}"
                ])
                
                food_details.append(food_in)
                button_infos.append({
                    "label": f"Place Order for {food_obj.properties['food_name']}",
                    "key": f"order_{food_obj.properties['food_id']}",
                    "food_id": food_obj.properties['food_id'],
                    "food_name": food_obj.properties['food_name']
                })
            finally:
                weaviate_client.close()
            
        food_info = food_info + "\n\n".join(food_details)
        return [food_info, button_infos]
        
    except json.JSONDecodeError:
        return ["Invalid JSON response", None]
    except Exception as e:
        print(f"Error in text_response: {str(e)}")
        return [f"An error occurred: {str(e)}", None]
async def send_chat_request(prompt, user_location,user_id):
    tools_list = await initialize_mcp_session()
    agent_scratchpad = ""
    result = ""
    context = []
    history = ""
    querry_to_send = f"""Assume your an meal planner Assistant which collects all the information required to answer user query only .
      !!!!! Mandatorily follow this  !!!!!
       should answer only user queries related to food ,restaurants ,current location,nearest locations only any other user queries should not be responded !!!!!!!!!
       should gather all the information related to user query for food should have details of every food related to query 
       if the user query is related to food then bring all the information it is related to that food ids Mandatorily
        !!!!!!!!


    !!!!!  Mandatorily follow this !!!!
    if the user mentions for ordering food where the food id is given query then call the ordering tool if not then mention that the food id is not mentioned in query to order it .
      example : order me food with id F001 
      Thought : ordering the food with id F001
      Action  : place_order_with_food_id
    !!!!


   Bring the information needed to answer the user query as best as you can by doing step by step. You have access to the following tools:

{tools_list}


In each step should only use either one tool or neither as per user query  :

Thought: you should always think about what to do in each step 
Action: the action to take, should call only one tool from all the tools (just give the tool name)
Actioninput: what arguments you give for the tool you mentioned in Action Respond using JSON
... (this Thought/Action/Actioninput can repeat N times until you get all the information related to question)

!!!!! Mandatorily  maintain this for every response for using any tool only  !!!!!
you give Thought, Action and Actioninput as outputs in each of your response
 Respond using JSON of Thought, Action and Actioninput
!!!!!!!!!!!!!!

Use the following format for understanding the entire prompt:
user query : prompt given by the user 
tool_returned_output : we will perform the action as you given and keep the output of the action here in next continuation prompt in this.

!!!!!!!!!!
user query : user id is {user_id} my current location is {user_location}  get information need to answer this  "{prompt}"  
!!!!!!!!

!!!! Final Response !!!!!!
if you set Action to None that means your have all the infomation to Respond to user query 
you have all the information of food items if they are discussed in  the  in the Actioninput 

After getting all the information required to answer the user query should give this type of output in Js :
Thought: 
Action : None
Actioninput : if about some food is discused in the Thought then mention those ids in the list or else give empty list  example : ["1-3","2-3"] or []

!!!!!!!

This is an example how the final Response should be for questions 
example : -
user query : "give me details of the restaurant with id 1" 
Thought : I have bought the information of the restaurant with id 1 to answer the query 
Action : None 
Actioninput : []



If a tool execution error occurs:

    If the error is due to your own input, try to fix the format and run it again.
    If the issue can't be fixed, try once more.
    If it still fails, explain the error in the Thought, set Action to None, and set ActionInput to an empty list [].


This the past 2 Histories of this user use it if need as per the query :
{mcp.state.user_history}

!!!!!!!!!!!!!
    Recognize that history is ordered chronologically (older → newer).

    Use recent messages when they contain important context.

    Maintain continuity in multi-turn conversations.
!!!!!!!!!!!!!

Begin!
""" 
    
    print(querry_to_send)
    for i in range(8) :
        history = history + "   \n  \n   " + agent_scratchpad
        payload = {
               "messages" : [{"role" : "user" , "content" : querry_to_send + history}]
               }

        json_payload = json.dumps(payload)
        curl_command = [
            'curl',
            '-X', 'POST',
            '--header', 'Content-Type: application/json',
            '--data', json_payload,
            quin_url
        ]

        try:
            result = subprocess.run(curl_command, 
                                capture_output=True, 
                                text=True, 
                                check=True)
            output = result.stdout
            response = json.loads(output)
            print(response)
            thought = ""
            action = ""
            action_input = ""
            tool_returned_output = ""
            try:
                content = json.loads(response['choices'][0]['message']['content'])
                thought = content.get("Thought", "")
                action = content.get("Action", "")        
                action_input = content.get("Actioninput", "")
                if( (action ==  "none" or action == "None")):
                    agent_scratchpad = json.dumps({
                    "Thought": thought,
                    "Action": action,
                    "Actioninput": action_input,
                })
                    history = history + "   \n  \n   " + agent_scratchpad 
                    break 
                
                else:
                    action_input_str = str(action_input) 
                    processed_input = None
                    
                    try:
                       
                        if isinstance(action_input, dict):
                            processed_input = action_input
                            
                       
                        elif isinstance(action_input, str):
                          
                            cleaned_input = action_input.strip()
                            
                          
                            if cleaned_input in ['{}', '""', "''"]:
                                processed_input = {}
                            else:
                                
                                cleaned_input = cleaned_input.replace("''", '"').replace("'", '"')
                                
                               
                                try:
                                    processed_input = json.loads(cleaned_input)
                                except json.JSONDecodeError:
                                  
                                    if not cleaned_input.startswith('{'):
                                        cleaned_input = '{' + cleaned_input + '}'
                                    try:
                                        processed_input = json.loads(cleaned_input)
                                    except json.JSONDecodeError:
                                        raise ValueError("Malformed JSON in Actioninput")
                        
                
                        if not isinstance(processed_input, dict):
                            raise ValueError("Actioninput must evaluate to a dictionary")
                            
                        print(f"Processed action_input: {processed_input}")
                        
                        if action and action != "None":       
                            tool_returned_output = await call_tool(action, processed_input)
                            if action == "get_current_location"  :  
                                user_location= tool_returned_output
                                tool_returned_output = "this is the current location of the user" + tool_returned_output
                        else:
                            tool_returned_output = "Action not specified or is None"
                            
                    except ValueError as e:
                        tool_returned_output = f"Actioninput format error: {str(e)}. Original: {action_input_str}"
                    except Exception as e:
                        tool_returned_output = f"Error calling tool: {str(e)}"
            
            except Exception as e:
                tool_returned_output = f"this {e} not set properly in json format"
            
            print(f"Thought: {thought}")
            print(f"Action: {action}")
            print(f"Actioninput: {action_input}")            
            print(f"Observation: {tool_returned_output}")
            
            agent_scratchpad = json.dumps({
                "Thought": thought,
                "Action": action,
                "Actioninput": action_input,
                "tool_returned_output": tool_returned_output
            })
            
            print("\n")
            print(agent_scratchpad)
            print("\n")

        except subprocess.CalledProcessError as e:
            tool_returned_output = f"Error: {e.stderr}"
            agent_scratchpad = json.dumps({
                "Thought": "",
                "Action": "",
                "Actioninput": "",
                "tool_returned_output": tool_returned_output
            })
        except json.JSONDecodeError as e:
            tool_returned_output = f"Error parsing JSON: {e}"
            agent_scratchpad = json.dumps({
                "Thought": "",
                "Action": "",
                "Actioninput": "",
                "tool_returned_output": tool_returned_output
            })
    print("hellooo")
    try:
        content = await final_prompt(history, prompt)
        thought = content.get("FinalResponse", "")
        action_input = content.get("Actioninput", "")
        mcp.state.user_history.append(json.dumps({
        "user_query": prompt,
        "Assistant_Response": {
            "FinalResponse": thought,
            "List of food Ids ": action_input
        }
    }))
        if len(mcp.state.user_history) > 2:
            mcp.state.user_history.pop(0)  
        response = {
            "content": content,
            "user_location": user_location
        }
        json_response = json.dumps(response, indent=2) 
        response =   await text_response(json_response)
        return response
    except:
        return content
        
@mcp.get("/{prompt}")
async def root(prompt: str):
    try:
        user_location = "unknown"
        user_id = "102"
        result = await send_chat_request(prompt,user_location,user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@mcp.post("/chat/")
async def chat(request: Request):
    try:
        # Extract JSON data from the request
        request_data = await request.json()
        
        # Get individual fields
        user_location = request_data.get("user_location")
        prompt = request_data.get("prompt")
        user_id = request_data.get("user_id")
        
        # Validate required fields
        if not user_location or not prompt:
            raise HTTPException(status_code=400, detail="Missing required fields (user_location or prompt)")
        
        # Process the request (replace with your actual logic)
        result = await send_chat_request(prompt, user_location,user_id)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@mcp.post("/order/")
async def order(request: Request):
    try:
        # Extract JSON data from the request
        request_data = await request.json()
        food_id =request_data.get("food_id")
        user_id = int(request_data.get("user_id"))
        client = None  # Initialize client variable
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
            return "you does not have enough money to order the food"

        updated_data_user = {"wallet_balance": user_wallet_bal - food_price}
        user_coll.data.update(
            uuid=user_uuid,
            properties=updated_data_user,  
        )
        order_data = {
            "user_id": user_id,
            "food_id": food_id,
            "restaurant_name": food_obj.properties["restaurant_name"],
            "food_name": food_obj.properties["food_name"],
            "time": str(datetime.now()),
            "price": int(food_obj.properties["price_rupee"])
        }
        print(food_obj.properties["price_rupee"])
        orders_coll = client.collections.get("Orders")
        orders_coll.data.insert(properties=order_data)
        return f"Your order has been placed and your current balance is {user_wallet_bal - food_price}"
    
    except Exception as e:
        return f"cannot able to connect the database: {str(e)}"
    
    finally:
        if client is not None:
            client.close()  # Ensure client connection is closed


@mcp.post("/ordered/")
async def ordered(request: Request):
    try:
        request_data = await request.json()
        user_id = int(request_data.get("user_id"))
        
        if not user_id:
            raise HTTPException(status_code=400, detail=str(e))

        client = None
        try:
            client = weaviate.connect_to_local(
                host="localhost",
                port=8080,
                grpc_port=50051,
            )
            user_uuid = generate_uuid5(user_id)
            user_coll = client.collections.get(user_class)
            if not (user_obj := user_coll.query.fetch_object_by_id(user_uuid)):
                return "User with this ID is not present in the database"
            orders_coll = client.collections.get("Orders") 
            order_filter = Filter.by_property("user_id").equal(user_id)
            user_orders = orders_coll.query.fetch_objects(
                filters=order_filter,
                limit=100  # or whatever number you need
            )    
            # Process and return the orders
            orders_list = []
            for order in user_orders.objects:
                orders_list.append({
                    "order_id": str(order.uuid),
                    "user_id": order.properties.get("user_id"),
                    "food_id": order.properties.get("food_id"),
                    "Restaurant_name": order.properties.get("restaurant_name"),
                    "Food_name": order.properties.get("food_name"),
                    "time" :order.properties.get("time"),
                    "price":str(order.properties.get("price"))
                    # Add other relevant fields from your schema
                })     
            orders_list.reverse() 
            return {"orders": orders_list,"balance" : user_obj.properties["wallet_balance"]}
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
            
        finally:
            if client is not None:
                client.close()
                
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@mcp.post("/delete/")
async def delete(request: Request): 
    mcp.state.user_history =  []
    return     
@mcp.get("/search")
async def search():
    try: 
        result = "happy"
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))