from openai import OpenAI
import os 
import json
from copy import deepcopy 
import dotenv 
dotenv.load_dotenv()
from utils import get_chatbot_response

class ClassificationAgent():

    def __init__(self):
        self.client = OpenAI(
            api_key = os.getenv("RUNPOD_TOKEN"),
            base_url = os.getenv("RUNPOD_CHATBOT_URL")
        )
        self.model_name = os.getenv("MODEL_NAME")
    
    def get_response(self, messages):
        messages = deepcopy(messages)
        system_prompt = """ 
        You are a helpful AI assistant for a coffee shop application. 

        Your task is to determine what agent should handle the user input. You have 3 agents to choose from:
        1. Details Agent : This agent is responsible for answering questions about the coffee shop, like location, delivery places, working hours, details about menu items. This agent can also respond to listing items in the menu items or by asking what we have.
        2. Order Taking Agent : This agent is responsible for taking orders from the user. He is responsable to have a conversation with the user about the order until it's complete. 
        3. Recommendation Agent : This agent is responsible for given recommendations to the user about what to buy. If the user asks for a recommendation, this agent should be used. 

        Your output should be in a structured json format like so. Each key is a string and each value is a string. Make sure to follow the format exactly:
        {
            "chain of thought": go over each of the agents above and write some of your thoughts about what agent is this input relevant to.
            "decision": Details Agent or Order Taking Agent or Recommendation Agent. Pick one of those, and only write the word.
            "message": leave the message empty.
    
        }
        """

        input_messages = [{
            "role": "system",
            "content" : system_prompt
        }] + messages[-2:]

        chatbot_output = get_chatbot_response(self.client, self.model_name, input_messages)
        output = self.postprocess(chatbot_output)
        return output
    
    def postprocess(self, output):
        output = json.loads(output)
        dict_output = {
            "role": "assistant",
            "content" : output["message"],
            "memory": {
                "agent": "classification_agent",
                "classification_decision": output["decision"]
            }
        }
        return dict_output
