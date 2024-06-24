import os

from langchain_openai import ChatOpenAI

from main import execute, plan

embedder = {
    "provider": "openai",
    "config": {
        "model": "jina-embeddings-v2-base-en",
        "api_key": os.getenv("JINA_API_KEY"),
        "api_base": "https://api.jina.ai/v1",
    },
}
llm = ChatOpenAI(
    base_url="https://api.openai.com/v1", api_key=os.getenv("OPENAI_API_KEY")
)

tasks_json = plan(
    "Do an online research and make a comparative list of Free and Open source LLMs with less than 10B parameters. Compare them on the scores on various bencmarks. Write summary and pick the best among them best of the comparative analysis.",
    llm=llm,
    embedder=embedder,
)
# with open("outputs/tasks.json") as f:
#     tasks_json = f.read()
execute(tasks_json, llm=llm, embedder=embedder)
