from langchain_core.prompts import ChatPromptTemplate
from ai.models import AIModel, AIModelProvider

llm = AIModel(AIModelProvider.OPENAI, "gpt-4.1-nano").get_llm()
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Write a short summary of the following in less than 10 words. "
            "Avoid using punctuation and special characters. "
            "Use numbers for calendar days. "
            "\n\n{input}",
        ),
    ]
)


def get_summary(user_input: str) -> str:
    """
    Get a summary of user input in short text to show in the chat list as the title.
    """
    try:
        return llm.invoke(prompt.format(input=user_input)).content
    except Exception as e:
        print(f"Error getting summary: {e}")
        return None
