import requests
import streamlit as st
import re
import json
import os

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

# Show a prominent welcome message with the Equitech logo when the app is loaded
equitech_logo_path = "/Users/user/Desktop/equitech.png"  # Adjust this path to your logo file

st.title("Welcome to Equitech Innovation Lab")

if os.path.exists(equitech_logo_path):
    st.image(equitech_logo_path, width=200)
else:
    st.error("Equitech logo not found. Please check the file path.")

st.write("Explore our Multi-Agent Health Chatbot below.")

# Initial user input: name, age, country
if "user_info" not in st.session_state:
    st.session_state.user_info = {}

if not st.session_state.user_info:
    st.session_state.user_info["name"] = st.text_input("What's your name?", help="Tell me your name so I can personalize your experience.")
    st.session_state.user_info["age"] = st.number_input("How old are you?", min_value=1, max_value=120, help="Your age helps me give better advice.")
    st.session_state.user_info["country"] = st.text_input("Which country are you from?", help="Knowing your country helps in providing region-specific advice.")
    if st.button("Submit"):
        st.write(f"Thank you, {st.session_state.user_info['name']}! Let's get started.")
else:
    user_name = st.session_state.user_info["name"]
    st.write(f"Welcome back, {user_name}! How can I assist you today?")

# Session state to store chat messages, agent responses, and feedback visibility
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent_outputs" not in st.session_state:
    st.session_state.agent_outputs = []

if "show_feedback" not in st.session_state:
    st.session_state.show_feedback = False

# Display existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=message.get("icon", "🤖")):
        st.markdown(message["content"])

# Sidebar with information about agents and interaction suggestions
with st.sidebar:
    st.header("Our Health Experts")
    st.write("🩺 **Doctor**: General medical advice")
    st.write("🧠 **Therapist**: Mental health support")
    st.write("🥗 **Dietician**: Nutrition guidance")
    st.write("💊 **Pharmacist**: Medication information")
    st.write("🏋️ **Sport Scientist**: Exercise recommendations")

    st.header("💡 Interaction Tips")
    if st.button("👤 Ask the Doctor"):
        st.info("You can ask the Doctor about symptoms, diagnosis, or treatment options.")
    if st.button("🥗 Consult the Dietician"):
        st.info("You can consult the Dietician for meal plans, nutrition advice, and dietary restrictions.")
    if st.button("💊 Check with the Pharmacist"):
        st.info("You can ask the Pharmacist about medication dosages, side effects, and interactions.")
    if st.button("🏋️ Get Fitness Tips from Sport Scientist"):
        st.info("You can ask the Sport Scientist for exercise routines, fitness plans, and injury prevention tips.")

# Create a chat input field to allow the user to enter a message
if prompt := st.chat_input("What is up? Ask me anything about health!"):
    # Store and display the current prompt
    st.session_state.messages.append({"role": "user", "content": prompt, "icon": "👤"})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Personalized response handling
    if prompt.lower() == "hello":
        st.session_state.messages.append({"role": "assistant", "content": f"Hello {user_name}! How can I help you today?", "icon": "🤖"})
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(f"Hello {user_name}! How can I help you today?")
    else:
        # Generate a response using the Flowise API
        response_data = query({"question": prompt})

        # Map each agent to a specific icon
        agent_icons = {
            "Nutritional app": "🍏",
            "Sport Scientist": "🏋️",
            "Dietician": "🥗",
            "Doctor": "🩺",
            "Therapist": "🧠",
            "Pharmacist": "💊",
            "assistant": "🤖",  # Fallback for the assistant's main response
        }

        # Track which agent types have already responded
        seen_agents = set()
        agent_responses = {}

        # Iterate over the agentReasoning field and display each agent's response if available
        if "agentReasoning" in response_data:
            agent_outputs = {}
            for agent in response_data["agentReasoning"]:
                agent_name = agent.get("agentName", "Unknown Agent")
                messages = agent.get("messages", [])
                icon = agent_icons.get(agent_name, "🤖")  # Fallback icon if agent not found

                # Check if this agent's advice has already been provided
                if agent_name not in seen_agents and messages:
                    seen_agents.add(agent_name)  # Mark this agent as having provided a response

                    # Display the agent's messages with the user's name included
                    for message in messages:
                        personalized_message = f"{user_name}, {message}"
                        st.session_state.messages.append({"role": agent_name, "content": personalized_message, "icon": icon})
                        agent_responses[agent_name] = personalized_message  # Save for summary output
                        agent_outputs[agent_name] = personalized_message  # Save agent output for download

            # Add agent outputs to session state
            st.session_state.agent_outputs.append({"prompt": prompt, "responses": agent_outputs})

            # Show feedback section after agent responds
            st.session_state.show_feedback = True

        # Generate a combined summary of all agent responses
        if agent_responses:
            summary_message = "Here's a summary of your personalized recommendations:\n\n"
            for agent_name, response in agent_responses.items():
                summary_message += f"**{agent_name}:** {response}\n\n"
            st.session_state.messages.append({"role": "assistant", "content": summary_message, "icon": "🤖"})
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(summary_message)

# Feedback section
if st.session_state.show_feedback:
    st.write("Was this answer helpful?")
    if st.button("👍 Yes"):
        st.success("Thank you for your feedback!")
        st.session_state.show_feedback = False
    elif st.button("👎 No"):
        st.warning("We'll try to do better next time.")
        st.session_state.show_feedback = False

# Option to download agent outputs
if st.session_state.agent_outputs:
    output_json = json.dumps(st.session_state.agent_outputs, indent=2)
    st.download_button(
        label="📥 Download Agent Outputs",
        data=output_json,
        file_name="agent_outputs.json",
        mime="application/json"
    )
