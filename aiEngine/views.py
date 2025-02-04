import os
import json
import logging
from dotenv import load_dotenv
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain.chains.conversation.memory import ConversationBufferMemory
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the Pydantic model for structured outputs
class GeneratedResponse(BaseModel):
    response: str
    action: str  # Added action field here

# Initialize Groq LLM
groq_llama3_llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0.7,
    groq_api_key=os.environ.get("GROQ_API_KEY"),
)

# Define the output parser
parser = JsonOutputParser(pydantic_object=GeneratedResponse)

# Memory to keep conversation context
memory = ConversationBufferMemory()

# Create a prompt template for JARVIS 
prompt = ChatPromptTemplate.from_messages([
    ("system", """
    You are JARVIS, an AI assistant created by Bello Ibukun King-David, a lead developer and co-founder at Nestegg, skilled in web development, mobile development, AI, and embedded systems.

    Your role is twofold:
    1. Process user commands related to energy management, providing actionable responses like "turn_on" or "turn_off" based on clear data and user input.
    2. Act as a personal assistant capable of answering general questions and engaging in casual conversation, keeping a professional yet friendly tone.

    If the user gives a **direct command** (e.g., "turn on the socket" or "turn off the socket"), you should immediately respond with the appropriate action (`turn_on` or `turn_off`) without asking for further confirmation, unless there is ambiguity in the input. Only seek user input when:
    - The command is unclear or incomplete.
    - Additional information is required to determine the appropriate action.
    - The action might have significant consequences or risks.

    Your responses must be clear, structured, and concise, reflecting Bello's technical expertise and decision-making style. You should always aim to explain things in simple terms, but with precision and clarity, avoiding unnecessary jargon.

     
    Important:
    - Do not include any text outside of the JSON block.
    - If you need to explain something, include it inside the "response" field.
    - Avoid conversational introductions or text outside the JSON format.

    Your response must be wrapped in a JSON object and follow this format exactly:
    {{
        "response": "<Your response text>",
        "action": "<ask_user, turn_on, turn_off>"
    }}
 
    Examples:
    - For a direct command to turn on a system: "Turning the socket on as requested."
    - For a direct command to turn off a system: "Turning the socket off as requested."
    - If the system requires user input: "Based on the energy consumption data provided, would you like to turn the system on or off?"

    Your tone should be professional, clear, and friendly, providing actionable choices when necessary but prioritizing immediate execution for explicit commands.
    """),
    ("user", "{input}")
])


# Chain for intelligent responses
chain = prompt | groq_llama3_llm | parser

# Django views
def index(request):
    return JsonResponse({'message': 'JARVIS AI is up and running!'})

@csrf_exempt
def interact_with_ai(request):
    if request.method == 'POST':
        try:
            # Parse incoming JSON
            data = json.loads(request.body)
            user_input = data.get('input', '')

            if not user_input:
                return JsonResponse({'error': 'Input is required.'}, status=400)

            # Generate response using LangChain
            try:
                # Determine action based on user input
                action = None
                if "turn on" in user_input:
                    action = "turn_on"
                elif "turn off" in user_input:
                    action = "turn_off"

                # Invoke the AI chain with the action
                result_raw = chain.invoke({"input": user_input, "action": action})

                # Log and print the raw AI output for debugging
                logger.info(f"Raw AI Output: {result_raw}")
                print(f"Raw AI Output: {result_raw}")

                # Parse the response
                if isinstance(result_raw, dict) and 'response' in result_raw:
                    response_text = result_raw['response']
                    action = result_raw.get('action', None)  # action should now come from the LLM
                else:
                    # Handle non-conforming output
                    logger.warning(f"Unexpected AI response format: {result_raw}")
                    print(f"Unexpected AI response format: {result_raw}")
                    response_text = "Invalid response format from AI."
                    action = None

            except Exception as parse_error:
                logger.error(f"Error during chain invocation or output parsing: {parse_error}")
                print(f"Error during chain invocation or output parsing: {parse_error}")
                response_text = "I'm sorry, I encountered an issue processing your request."
                action = None

            # Prepare the response payload
            response_payload = {
                'response': response_text,
                'action': action
            }

            return JsonResponse(response_payload, status=200)

        except json.JSONDecodeError:
            logger.error("Invalid JSON format in request.")
            print("Invalid JSON format in request.")
            return JsonResponse({'error': 'Invalid JSON format.'}, status=400)
        except Exception as e:
            logger.exception("Unexpected error occurred.")
            print(f"Unexpected error occurred: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid HTTP method. Use POST.'}, status=405)
