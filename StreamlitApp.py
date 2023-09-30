import streamlit as st
from langchain.llms import GooglePalm
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.callbacks import get_openai_callback
from langchain.chains import ConversationChain

def count_tokens(chain, query):
    with get_openai_callback() as cb:
        result = chain.run(query)
        print(f'Spent a total of {cb.total_tokens} tokens')
    return result

def load_json_file(file_path):
    with open(file_path, 'r') as json_file:
        json_string = json_file.read()
    return json_string


st.title("Fotrofy Bot - Nutria Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

llm = GooglePalm(
    model='models/chat-bison-001',
    temperature=0,
    max_output_tokens=1024,
    google_api_key='AIzaSyA1fu-ob27CzsJozdr6pHd96t5ziaD87wM'
)


conversation_buf = ConversationChain(
    llm=llm,
    memory=ConversationBufferMemory()
)

user_data = load_json_file('CUST_PROFILE.json')

initial_message = f'''Act like a expert diet chatbot only use given formulas and user data to continue the chat:

Calculations :

### Recommended Calories Calculations:

**Step 1: BMR Calculation**
- For Men:
  - BMR = (10 × weight in kg) + (6.25 × height in cm) - (5 × age in years) + 5
- For Women:
  - BMR = (10 × weight in kg) + (6.25 × height in cm) - (5 × age in years) - 161

**Step 2: Calculate Calories Needed Based on Activity Level**
- Sedentary (No Exercise):
  - Multiplier: 1.2
- Lightly Active (Walking, Yoga, etc):
  - Multiplier: 1.375
- Moderately Active (Training around 3 times a week):
  - Multiplier: 1.55
- Super Active (Training more than 3 times a week):
  - Multiplier: 1.7

In cases where customer input is not available (e.g., Healthians), a default multiplier of 1.375 is recommended.

**Step 3: Adjust Calories for Specific Goals**
- Weight Loss: Reduce by 500 calories
- Weight Maintenance: Reduce by 200 calories
- Muscle Building: No reduction (0 calories)

In cases where specific goals are not provided, such as in the tie-up with Healthians, the following logic is used:
- If BMI is less than 23, reduce by 200 calories
- If BMI is more than 23, reduce by 500 calories

UserData : {user_data}'''

initial_message = conversation_buf(initial_message)

# Function to get response from Google Palm
def get_google_palm_response(query):
    response = count_tokens(conversation_buf, query)
    return response

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = get_google_palm_response(prompt)
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(f"Assistant: {response}")
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": f"Assistant: {response}"})
