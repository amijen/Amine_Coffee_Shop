# Amine_Coffee_Shop ☕️
After arriving in Paris in 2025, driven by my love for coffee, I decided to launch this personal project inspired by the works of [M. Abdullah Tarek and M. Chibuzor Nwachukwu](https://github.com/abdullahtarek/coffee_shop_customer_service_chatbot/tree/main). **This ongoing project** explores the intersection between AI agents, Large Language Models (LLMs), and Retrieval-Augmented Generation (RAG). My main contribution lies in prompt engineering and improving the generalization capabilities of the chatbot’s responses. I designed and iteratively refined prompts to handle a wide variety of user queries related to the coffee shop context from taking orders and answering detailed menu questions to providing personalized recommendations. \
Through this work, I gained hands-on experience with LLM-based conversational systems, AI agent design, and contextual retrieval mechanisms, making the project a deeply enriching exploration of intelligent customer interaction systems.
# 🎯 Project Overview
The goal of the project is to:
* Block irrelevant or harmful questions using a Guard Agent for safe interactions.
* Answer questions about menu items and our coffee shop based on **RAG system**.
* Recommend personalized products based on market basket analysis recommendation engine.
* Take client's order for specific product(s).
# 🧠 Chatbot Agent Architecture
<img width="1286" height="682" alt="image" src="https://github.com/user-attachments/assets/b56449d4-525f-4efc-86b7-ac618b2fcfad" />

🤖 Chatbot Reasoning
In this project, we have 6 steps: 
1. **User input:** here the client asks for something.
2. **Guard Agent**: It acts as a defense. It checks whether the question asked by the customer is relevant to the coffee shop or not. If it is an unsafe question, it blocks it and asks for a new question.
3. **Input Classifier Agent:** This agent classify the needed agent to answer for user's qurstion into one of three categories: order agent, recommendation agent, or details agent. This step is developed using chain-of-thought (CoT).
4. **Order Agent**: This agent is responsible for taking client's order. 
5. **Details Agent (RAG System)**: Powered by a Retrieval-Augmented Generation (RAG) system, the Details Agent answers specific customer questions about the coffee shop, including product components, prices... It retrieves information from vector databases using Pinecone environment.
6. **Recommendation Agent:** Using market basket recommendation engine technique, this agent helps the customer with its order. It can recommend him a new product or what to take with an ordered one.
# 📂 Directory Structure
├── Amine_Coffee_Shop \
│ ├── api/ # Chatbot API for agent-based system \
│ └── dataset # Dataset for training recommendation engine   
│ └── products # Product data (names, prices, descriptions)  \
|  └── build_vector_database.ipynb # Builds vector database for RAG model  \
|  └── recommendation_engine_training.ipynb # Trains recommendation engine \
└── README.md # You're here! \
# Refrence Links
* [M. Abdullah Tarek and M. Chibuzor Nwachukwu GitHub](https://github.com/abdullahtarek/coffee_shop_customer_service_chatbot/tree/main): Our project is inspired from their work.
* [Pinecone](https://www.pinecone.io/)
* [Hugging Face](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct): Hugging Face Models - Repository for Llama LLms, a state-of-the-art NLP model used in our chatbot.
