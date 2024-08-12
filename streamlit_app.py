import requests
import streamlit as st
import re

API_URL = "https://innovation-institute-flowise.onrender.com/api/v1/prediction/8284332b-ce69-4909-993f-4b1c05a1f04c"
headers = {"Authorization": "Bearer iy-0IVxxXuZVD9s3vdxc0V7duv6RUeraw2MpsnetfLU"}

def query(payload):
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Check if the request was successful
        return response.json()      # Try to parse JSON response
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err}")
        return {}
    except requests.exceptions.RequestException as req_err:
        st.error(f"Request error occurred: {req_err}")
        return {}
    except ValueError as json_err:
        st.error(f"JSON decoding error: {json_err}")
        st.write("Response content:", response.text)  # Print the raw response for debugging
        return {}

# Show title and description
st.title("🏥 Multi-Agent Health Chatbot")
st.write(
    "This chatbot uses a multi-agent system to provide health-related information. "
    "The system includes specialized agents: Doctor, Therapist, Dietician, Pharmacist, and Sport Scientist."
)


# Create a session state variable to store the chat messages. This ensures that the
# messages persist across reruns.
if "messages" not in st.session_state:
    st.session_state.messages = []
    
#Display the existing chat messages via `st.chat_message`.
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=message.get("icon", "🤖")):
        st.markdown(message["content"])
        
        
#create a chat input field to allow the user to enter a message. This will display
# automatically at the bottom of the page.
if prompt := st.chat_input("What is up?"):
 
    # Store and display the current prompt.
    st.session_state.messages.append({"role": "user", "content": prompt, "icon": "👤"})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
 
    # Generate a response using the Flowise API.
    response_data = query({"question": prompt})
    print(response_data)
 
    # Map each agent to a specific icon.
    agent_icons = {
        "Nutritional app": "🍏",
        "Sport Scientist": "🏋️",
        "Dietician": "🥗",
        "Doctor": "🩺",
        "Therapist": "🧠",
        "Pharmacist": "💊",
        "assistant": "🤖",  # Fallback for the assistant's main response
    }
 
    # Iterate over the agentReasoning field and display each agent's response if available.
    if "agentReasoning" in response_data:
        for agent in response_data["agentReasoning"]:
            agent_name = agent.get("agentName", "Unknown Agent")
            messages = agent.get("messages", [])
            icon = agent_icons.get(agent_name, "🤖")  # Fallback icon if agent not found
 
            # Display the agent's messages if they exist
            if messages:
                for message in messages:
                    st.session_state.messages.append({"role": agent_name, "content": message, "icon": icon})
                    with st.chat_message(agent_name, avatar=icon):
                        st.markdown(f"**{agent_name}:** {message}")
 
    # Always display the overall assistant's response (supervisor's summary).
    response_content = response_data.get("text", "Sorry, I couldn't generate a response.")
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(response_content)
    st.session_state.messages.append({"role": "assistant", "content": response_content, "icon": "🤖"})



# Add a sidebar with information about the agents
with st.sidebar:
    st.header("Our Health Experts")
    st.write("🩺 **Doctor**: General medical advice")
    st.write("🧠 **Therapist**: Mental health support")
    st.write("🥗 **Dietician**: Nutrition guidance")
    st.write("💊 **Pharmacist**: Medication information")
    st.write("🏋️ **Sport Scientist**: Exercise recommendations")
