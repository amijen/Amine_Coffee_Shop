# To test agents when developing 
from guard_agent import GuardAgent
from classification_agent import ClassificationAgent
from details_agent import DetailsAgent
from agent_protocole import AgentProtocol
from recommendation_agent import RecommendationAgent
from order_taking_agent import OrderTakingAgent
import os 
import pathlib 

folder_path = pathlib.Path(__file__).parent.resolve()

def main():
        guard_agent = GuardAgent()
        classification_agent = ClassificationAgent()
        agent_dict : dict[str, AgentProtocol] = {
            "Details Agent" : DetailsAgent(),
            "Recommendation Agent": RecommendationAgent(
                'recommendation_objects/apriori_recommendations.json',
                'recommendation_objects/popularity_recommendation.csv'
            ),
            "Order Taking Agent": OrderTakingAgent()
        }
        messages = []
        test=True
        while test==True: 
            os.system("cls" if os.name == "nt" else "clear")
            print("\n Print Messages")
            for message in messages: 
                print(f"{message["role"]}:{message["content"]}")
            
            # Get use input 
            prompt = input("User input: ")
            messages.append({
                "role":"user",
                "content" : prompt
            })
            # Get guard agent's response 
            guard_agent_response = guard_agent.get_response(messages)
            if guard_agent_response["memory"]["guard_decision"] == "not allowed":
                messages.append(guard_agent_response)
                continue
            print("From Guard to Classification")
            # Get classifiation Agent's response : what is the type of agent that we need to use?
            classification_agent_response = classification_agent.get_response(messages)
            print(classification_agent_response)
            chosen_agent = classification_agent_response["memory"]["classification_decision"]
            print(f"The chosen agent: {chosen_agent}")

            # Get the chosen agent's response 
            agent = agent_dict[chosen_agent]
            response = agent.get_response(messages)
            print(response["content"])
            messages.append(response)


if __name__=="__main__":
        main()


