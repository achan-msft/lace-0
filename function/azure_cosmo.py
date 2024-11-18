# working in progress !!!!! 

#  Cosmo CRUD
import openai
import tiktoken
from azure.cosmos import CosmosClient
import uuid

# Set up OpenAI API
openai.api_key = "your-azure-api-key"
openai.api_base = "https://your-resource-name.openai.azure.com/"
openai.api_version = "2023-06-01"  # Use appropriate API version

# Set up Cosmos DB
COSMOS_ENDPOINT = "your-cosmos-db-endpoint"
COSMOS_KEY = "your-cosmos-db-key"
COSMOS_DATABASE = "your-database-name"
COSMOS_CONTAINER = "chatHistory"
client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
database = client.get_database_client(COSMOS_DATABASE)
container = database.get_container_client(COSMOS_CONTAINER)

# Set the model and token limit
MODEL = "gpt-4"
TOKEN_LIMIT = 8192  # GPT-4 8K model token limit

# Initialize tiktoken encoder for the model
encoder = tiktoken.get_encoding("gpt-4")

# Function to count the number of tokens in a message
def count_tokens(messages):
    total_tokens = 0
    for message in messages:
        total_tokens += len(encoder.encode(message['content']))
    return total_tokens

# Function to get conversation history from Cosmos DB
def get_conversation_history(user_id):
    query = f"SELECT * FROM c WHERE c.user_id = '{user_id}'"
    items = list(container.query_items(query=query, enable_cross_partition_query=True))
    return items[0]["messages"] if items else []

# Function to save conversation history to Cosmos DB
def save_conversation_history(user_id, conversation_history):
    conversation_id = str(uuid.uuid4())  # Unique conversation ID
    document = {
        "id": conversation_id,
        "user_id": user_id,
        "messages": conversation_history
    }
    container.upsert_item(document)

# Function to truncate conversation history based on token limits
def trim_conversation_history(messages, token_limit):
    # Trim messages from the beginning until we are under the token limit
    while count_tokens(messages) > token_limit:
        messages.pop(0)
    return messages

# Function to get the model's response while managing conversation history
def get_model_response(user_id, user_input):
    # Retrieve conversation history
    conversation_history = get_conversation_history(user_id)

    # Add the user's new message
    conversation_history.append({"role": "user", "content": user_input})

    # Trim history if it exceeds the token limit
    conversation_history = trim_conversation_history(conversation_history, TOKEN_LIMIT)

    # Call the OpenAI model
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=conversation_history
    )

    # Get assistant's response
    assistant_reply = response['choices'][0]['message']['content']

    # Add the assistant's response to the history
    conversation_history.append({"role": "assistant", "content": assistant_reply})

    # Save the updated conversation history to Cosmos DB
    save_conversation_history(user_id, conversation_history)

    return assistant_reply

# Example user interaction
user_id = "user123"
user_input = "Hello, how are you?"
response = get_model_response(user_id, user_input)
print(f"Assistant: {response}")

user_input = "What's the weather like today?"
response = get_model_response(user_id, user_input)
print(f"Assistant: {response}")

# 
# Overview of the Solution:
# Store the conversation history in Cosmos DB: Each conversation with a user will be stored as a document in a Cosmos DB container.
# Retrieve the conversation history: For each user interaction, you'll retrieve the history from Cosmos DB to send along with the current message to the model.
# Update the Cosmos DB: After getting the response from the model, you will update the Cosmos DB with the new conversation state.

# --------------------------------------------------------------------------------------------------------------------------
# 1. Token Limit per Model:
# Each model has a maximum token limit, which includes both the input (your conversation history) and the output (the response from the model). The most common models and their token limits are:

# GPT-3.5-turbo: ~4,096 tokens
# GPT-4 (8K version): ~8,192 tokens
# GPT-4 (32K version): ~32,768 tokens
# A token is roughly equivalent to a few characters of text, so 1,000 tokens might be around 750 words (it depends on the language and structure of the text). When managing long conversations, you need to make sure the combined token count of the history and the model's response does not exceed this limit.

# 2. How to Manage Long Conversations:
# Truncating Conversation History:
# As the conversation grows, you'll want to trim the history to fit within the model's token limit. The most common strategies are:

# Trim from the beginning: Keep only the most recent exchanges, discarding earlier parts of the conversation.
# Summarization: Instead of sending the entire history, you can periodically summarize the conversation and send the summary along with the latest message.
# Practical Example:
# You might decide to only keep the last X messages in the history or to use summaries. Here's an approach you can use based on the number of tokens consumed by the conversation.

# Example Strategy:
# Calculate Token Usage: Use the tiktoken library (provided by OpenAI) to estimate the number of tokens in your conversation history.
# Trim the History: Remove older messages if the token count exceeds the model’s limit, keeping as much of the recent conversation as possible.
# Summarize the History (optional): If the conversation exceeds a reasonable length, you can periodically ask the model to summarize the conversation so far and use that summary to reduce the token count.





# How It Works:
# Counting Tokens: The count_tokens() function estimates how many tokens are used in the entire conversation history. It uses the tiktoken library, which is optimized for token counting with OpenAI's models.

# Trimming the History: If the token count exceeds the model's limit (TOKEN_LIMIT), the trim_conversation_history() function removes older messages from the conversation history until the token count is within limits.

# Conversation Updates: After each new user input and model response, the conversation history is updated and saved back to Cosmos DB.

# 4. When to Summarize:
# If you're dealing with extremely long conversations, it might be better to periodically ask the model to summarize the conversation so far. This can be done as follows:

# Ask for a summary: You can periodically prompt the model with something like:

# "Summarize our conversation so far in a few sentences."
# Use the summary: Replace the entire conversation history with the summary, keeping the latest few interactions.

# This allows you to keep the conversation going without hitting token limits while still maintaining useful context.

# 5. Considerations:
# Truncation: Truncating from the beginning means that you lose some context, which might impact the model's ability to provide accurate responses over long sessions. This is why summarization is often a good alternative when history length is high.
# Cosmos DB: This implementation keeps the full history in Cosmos DB, so you can always access the complete chat log, even if the current session has truncated parts of it due to token limits.
# Conclusion:
# For long conversations, you will need to carefully manage the number of tokens passed to the model. By trimming the conversation history and periodically summarizing, you can ensure that the model can continue to provide relevant responses without exceeding its token limits.

# Let me know if you'd like further examples or adjustments!



