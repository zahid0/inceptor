from langchain_groq import ChatGroq
from main import main
main(
        "Do an online research to find the freelancing platforms for software engineers, devops and AI/ML engineers. Make a comprehensive report in markdown format, highlighting the salient features of each. Highlight pro and cons of each. The report should facilitate easy comparison as well as information to onboarding on the platform",
        llm = ChatGroq(model="llama3-70b-8192", max_tokens=2048)
)
