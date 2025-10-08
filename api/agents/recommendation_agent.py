from dotenv import load_dotenv
import os
import json
from utils import get_chatbot_response
from openai import OpenAI
from copy import deepcopy 
import pandas as pd 

load_dotenv()

class RecommendationAgent():

    def __init__(self, apriori_recommendation_path, popular_recommendation_path):
        self.client = OpenAI(
            api_key=os.getenv("RUNPOD_TOKEN"),
            base_url=os.getenv("RUNPOD_CHATBOT_URL")
        )
        self.model_name = os.getenv("MODEL_NAME")
        with open(apriori_recommendation_path, 'r') as file: 
            self.apriori_recommendations = json.load(file)

        self.popular_recommendation = pd.read_csv(popular_recommendation_path)
        self.products = self.popular_recommendation['product'].tolist()
        self.product_categories = list(set(self.popular_recommendation['product_category'].tolist()))


    def get_apriori_recommendation(self, products, top_k = 2): 
        apriori_lower = {k.lower(): v for k, v in self.apriori_recommendations.items()}
        recommendation_list = []
        for product in products: 
            product = product.lower()
            if product in apriori_lower:
                recommendation_list += apriori_lower[product]

        # Sort recommendation list by confidence 
        recommendation_list = sorted(recommendation_list, key = lambda x: x['confidence'], reverse = True)
        recommendations = []
        recommendation_per_category = {}
        for recommendation in recommendation_list: 
            if recommendation in recommendations: 
                continue
            # Limit 2 recommendations per category 
            product_category = recommendation['product_category']
            if product_category not in recommendation_per_category : 
                recommendation_per_category[product_category] = 0 
            
            if recommendation_per_category[product_category] >=2:
                continue
            recommendation_per_category[product_category] += 1 
            # Add recommendation
            recommendations.append(recommendation['product'])
            if len(recommendations) >= top_k:
                break
        
        return recommendations

    def get_popular_recommendation(self, product_categories = None, top_k = 2): 
        """ Ask for popular recommendation per category """
        recommendation_df = self.popular_recommendation

        if type(product_categories) == str:
            product_categories = [product_categories.lower()]
        
        if product_categories is not None: 
            recommendation_df = self.popular_recommendation[self.popular_recommendation['product_category'].str.lower().isin(product_categories)] 
        recommendation_df = recommendation_df.sort_values('number_of_transactions', ascending = False)
        if recommendation_df.shape[0] == 0:
            return []
        recommendations = recommendation_df['product'].tolist()[:top_k]
        return recommendations
    
    def recommendation_classification(self, messages):
        system_prompt = """ 
        You are a helpful AI assistant for a coffee shop application which serves drink and pastries. We have 3 types of recommendations: 

        1. Apriori Recommendations: These are recommendations based on the user's order history. We recommend items that are frequently bought together with the items in the user's order.
        2. Popular Recommendations: These are recommendations based on the popularity of items in the coffee shop. We recommend items that are popular among customers. The user can also ask to recommend him an item to buy with a given product. For example, he can ask to recommend him a product that goes with a "croissant". He can ask to compare between two products and you must choose based on the popularity of the item. If he asked to compare between two products and one of them does not exist in our market, tell him "Sorry, we do not have (name the unavailable product), we suggest you to take (the available product).".
        3. Popular Recommendations by Category: Here the user asks to recommend them product in a category. For example, he asks :" what coffee do you recommend me to get?". We recommend items that are popular in the category of the user's requested category. In the given example, the category is "coffee". The user is free to write it with lower or upper cases. For example, "coffee", "Coffee", and "coFfee" have all the same category "Coffee".

        Here is the list of items in the coffee shop: 
        """+ ",".join(self.products) + """
        Here is the list of categories we have in the coffee shop:
        """ + ",".join(self.product_categories) + """

        Your task is to determine which type of recommendation to provide based on the user's message. 

        Your output should be in a structured json format like so. Each key is a string and each value is a string. Make sure to follow the format exactly:
        {
            "chain of thought": Write down your critical thinking about what type of recommendation is this input relevant to.
            "recommendation_type": Apriori Recommendations or Popular Recommendations or Popular Recommendations by Category. Pick one of those and only write the word. 
            "parameters": This is a python list. It is either a list of items for apriori recommendations or a list of categories for popular by category recommendations. Leave it empty for popular recommendation. Make sure to use the exact strings from the list of items and categories above.
        }
        """
        messages = deepcopy(messages)
        input_messages = [
            {
                "role" : "system",
                "content" : system_prompt
            }
        ] + messages[-3:]

        chatbot_response = get_chatbot_response(self.client, self.model_name, input_messages)
        output = self.postprocess_classification(chatbot_response)
    
        return output
    
    def postprocess_classification(self, output):
        output = json.loads(output)
        dict_output = {
            "recommendation_type" : output["recommendation_type"],
            "parameters": output["parameters"],
        }
        return dict_output
    
    def get_recommendations_from_order(self, messages, order):
        products = []
        for product in order: 
            products.append(product['item'])
        
        recommendations = self.apriori_recommendations(products)
        recommendations_str = ", ".join(recommendations)
        system_prompt = """ 
        You are a helpful AI assistant for a coffee shop which serves drinks and pastries. 
        Your task is to recommend items to the users based on their input messages. You need also to respond in a friendly but concise way, and put it an unordered list with a very small description.

        I will provide what items you should recommend to the user based on their order in the user message.
        """ 

        prompt = f""" 
        {messages[-1]["content"]}

        Please recommend me those items exactly: {recommendations_str}
       """
        
        messages[-1]["content"] = prompt 
        input_messages = [
            {
                "role" : "system",
                "content" : system_prompt
            }
        ] + messages[-3:]

        chatbot_output = get_chatbot_response(self.client, self.model_name, input_messages)
        output = self.postprocess(chatbot_output)
        return output
    
    def get_response(self, messages):
        messages = deepcopy(messages)
        recommendation_classification = self.recommendation_classification(messages)
        recommendation_type = recommendation_classification["recommendation_type"]
        recommendations = []
        if recommendation_type == "Apriori Recommendations":
            recommendations = self.get_apriori_recommendation(recommendation_classification["parameters"])
        elif recommendation_type == 'Popular Recommendations':
            recommendations = self.get_popular_recommendation()
        elif recommendation_type == "Popular Recommendations by Category":
            recommendations = self.get_popular_recommendation(recommendation_classification["parameters"])

        if recommendations == []:
            return {
                "role": "assistant",
                "content" : "Sorry, I can't help with that recommendation. Can I help you with something else."
            }
        # Respond to user
        recommendations_str = ", ".join(recommendations)
        system_prompt = f""" 
        You are a helpful AI assistant for a coffee shop which serves drinks and pastries. 
        Your task is to recommend items to the users based on their input messages. You need also to respond in a friendly but concise way, and put it an unordered list with a very small description.

        I will provide what items you should recommend to the user based on their order in the user message.
        """ 
        prompt = f"""
        {messages[-1]["content"]}

        Please recommend me those items exactly: {recommendations_str}
        """
        messages[-1]["content"] = prompt 
        input_messages = [{
            "role": "system",
            "content": system_prompt
        }] + messages[-3:]
        chatbot_response = get_chatbot_response(self.client, self.model_name, input_messages)
        output = self.postprocess(chatbot_response)
        return output

    def postprocess(self, output):
        output = {
            "role": "assistant",
            "content" : output,
            "memory": {
                "agent": "recommendation_agent"
            }
        }
        return output