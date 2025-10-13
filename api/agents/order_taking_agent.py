from dotenv import load_dotenv
import os
import json
from utils import get_chatbot_response, double_check_json_output
from openai import OpenAI
from copy import deepcopy 
load_dotenv()

class OrderTakingAgent():
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("RUNPOD_TOKEN"),
            base_url=os.getenv("RUNPOD_CHATBOT_URL")
        )
        self.model_name = os.getenv("MODEL_NAME")

    def get_response(self, messages):
        messagees = deepcopy(messages)

        system_prompt = """  
        You are a customer support bot for a coffee shop called "Amine Coffee Shop". 

        Here is the menu of this coffee shop: 

            Cappucin - €2.50
            Jumbo Savory Scone - €3.25
            Direct - €3.00
            Chocolate Chip Biscotti - €2.50
            Espresso shot - €2.00
            Hazelnut Biscotti - €2.75
            Chocolate Croissant - €2.75
            Dark chocolate (Drinking Chocolate) - €4.50
            Cranberry Scone - €3.50
            Croissant - €2
            Almond Croissant - €3.00
            Ginger Biscotti - €2.50
            Oatmeal Scone - €3.25
            Ginger Scone - €3.50
            Chocolate syrup - €1.50
            Hazelnut syrup - €1.50
            Carmel syrup - €1.50
            Sugar Free Vanilla syrup - €1.50
            Dark chocolate (Packaged Chocolate) - €3.00

        Things to not do: 
            1. Don't ask how to pay by cash or card.
            2. Don't tell the user to go to the counter.
            3. Don't tell the user to go to place to get the order.

        Your task is as follows:
        1. Take the user's order.
        2. Validate that all their items are in the menu.
        3. If an item is not in the menu let the user reorder and repeat back the remaining valid order.
        4. Ask them if they need anything else.
        5. If they do need anything else, repeat starting from step 3. If the user demanded to know the total price of his order, calculate the total and show him the result. If they do not want anything else, pass to step 6.
        6. Using the "order" object that is in the output. Make sure to hit all three points:
            a. List down all the items and their prices.
            b. Calculate the total and show the user the result. 
            c. Thank the user for the order and close the conversation with no more questions.
        
        The user message will contains a section called memory. This section will contain the following:
        1. "order"
        2. "step number"
        Please utilize this information to determine the next step in the process.

        Produce the following output without any additions, not a single letter outside of the structure below.
        Your output should be in a structured json format like so. Each key is a string and each value is a string. Make sure to follow the format exactly:
        {
            "chain of thought": Write down your critical thinking about what is the maximum task number the user is on right now. Then write your critical thinking about the user input and it's relation to the coffee shop process. Then write down your thinking about how you should respond in the response parameter taking into consideration the Things to not do section. Focus on the things that you should not do.
            "step number": Determine which task you are on based on the conversation.
            "order": This is going to be a list of json like so. [{"item": put the item name, "quantity": put the number that the user wants from this item, "price": put the total price of the item}]
            "response": Write the response to the user.
        }

        """

        last_order_taking_status = "" 
        for message_index in range(len(messages)-1,0,-1):
            message = messages[message_index]
            agent_name = message.get("memory", {}).get("agent","")
            if message["role"] == "assistant" and agent_name == "Order Taking Agent":
                step_number = message["memory"]["step number"]
                order = message["memory"]["order"]
                last_order_taking_status = f""" 
                step number: {step_number}
                order: {order}
                """
                break
        messages[-1]["content"] = last_order_taking_status + "\n" + messages[-1]["content"]
        input_messages = [{
            "role": "system",
            "content": system_prompt
        }] + messages
        chatbot_response = get_chatbot_response(self.client, self.model_name, input_messages)
        # double check json 
        chatbot_response = double_check_json_output(self.client,self.model_name,chatbot_response)
        output = self.postprocess(chatbot_response)
        return output
    
    def postprocess(self, output):
        output = json.loads(output)
        if type(output["order"]) == str: 
            output["order"] = json.loads(output["order"])
        response = output["response"]
        dict_output = {
            "role" : "assistant",
            "content": response,
            "memory": {
                "agent": "Order Taking Agent",
                "step number": output["step number"],
                "order": output["order"]
            }
        }
        return dict_output
