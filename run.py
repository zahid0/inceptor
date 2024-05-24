import os

from langchain_groq import ChatGroq

from main import execute

embedder = {
    "provider": "openai",
    "config": {
        "model": "jina-embeddings-v2-base-en",
        "api_key": os.getenv("JINA_API_KEY"),
        "api_base": "https://api.jina.ai/v1",
    },
}
llm = ChatGroq(model="llama3-8b-8192")

# tasks_json = plan(
#     "Do an online research to find the freelancing platforms for software engineers, devops and AI/ML engineers. Make a comprehensive report in markdown format, highlighting the salient features of each. Highlight pro and cons of each. The report should facilitate easy comparison as well as information to onboarding on the platform",
#     llm=llm,
#     embedder=embedder,
# )
with open("outputs/tasks.json") as f:
    tasks_json = f.read()
execute(tasks_json, llm=llm, embedder=embedder)
