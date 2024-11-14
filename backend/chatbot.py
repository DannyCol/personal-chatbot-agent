"""chatbot.py"""

import string
import os
import json
from dotenv import load_dotenv

from googleapiclient.discovery import build
from google.cloud import secretmanager
import google.generativeai as genai
import redis.asyncio as redis

load_dotenv()

GCP_CHAT_PROJECT_ID = os.environ["GCP_CHAT_PROJECT_ID"]
GCP_CHAT_ZONE = os.environ["GCP_CHAT_ZONE"]
GCP_CHAT_SECRETS_ID = os.environ["GCP_CHAT_SECRETS_ID"]
GCP_GKE_REDIS_NODEPORT = os.environ["GCP_GKE_REDIS_NODEPORT"]


# temp service discovery to use with node port
def cluster_endpoint_discovery(project: str, zone: str) -> str:
    """Gets the first endpoint of a node on any GKE cluster in the specified project and zone"""
    from googleapiclient import discovery

    service = discovery.build("compute", "v1")
    instances = service.instances().list(project=project, zone=zone).execute()["items"]
    for instance in instances:
        if instance["name"].startswith("gke"):
            endpoint = instance["networkInterfaces"][0]["networkIP"]
            return endpoint
    raise Exception("no gke node found")


# --- prompts --- #
PROMPT = """[System] You are a voice powered AI chatbot called "Gemini," designed to answer user's questions. \
Because your response is converted from text to audio, your responses must NOT use any special text formatting or emojis. \
You can access previous user interactions. You can access a search engine.\n"""
SEARCH_PROMPT = """[System] Answer 'yes' or 'no' ONLY: \
Is the following a question a search engine would be helpful for? """


class Chatbot:
    """A basic Python chatbot"""

    async def chatbot(
        self, model_name="models/gemini-1.5-flash-001", ground_with_google=True
    ):
        """Asyncronous class instantiation function"""
        # get secrets
        client = secretmanager.SecretManagerServiceAsyncClient()
        resource_name = f"projects/{GCP_CHAT_PROJECT_ID}/secrets/{GCP_CHAT_SECRETS_ID}/versions/latest"
        response = await client.access_secret_version(request={"name": resource_name})
        secret_info = json.loads(response.payload.data.decode().replace("'", '"'))

        genai.configure(api_key=secret_info["GEN_AI_API_KEY"])
        self.model = genai.GenerativeModel(model_name=model_name)
        self.embedding_model_name = "models/text-embedding-004"
        self.grounding = ground_with_google

        self.search_service = build(
            "customsearch", "v1", developerKey=secret_info["GOOGLE_SEARCH_API_KEY"]
        )
        self.search_cx = secret_info["GOOGLE_SEARCH_ENGINE_ID"]

        endpoint = cluster_endpoint_discovery(
            project=GCP_CHAT_PROJECT_ID, zone=GCP_CHAT_ZONE
        )
        self.rd = redis.Redis(
            host=endpoint, port=GCP_GKE_REDIS_NODEPORT, decode_responses=True
        )

        return self

    async def store_interaction(self, user_id, user_text, bot_text):
        """Store past conversation interaction in needed databases"""
        interaction_str = f"[User]: {user_text} [Gemini]: {bot_text} "
        # update the redis cache with a 5 minute TTL
        await self.rd.append(user_id, interaction_str)
        await self.rd.expire(user_id, 5 * 60)

    async def handle_question(self, user_id, text):
        """Main logic of chatbot"""
        # ask if it needs a search engine to answer query
        search_answer = (
            await self.model.generate_content_async(
                f'{SEARCH_PROMPT} Question: "{text}" [Gemini]: ',
                generation_config=genai.GenerationConfig(temperature=0.0),
            )
        ).text
        # get search engine result if applicable
        grounding_context = ""
        if self.__clean_yes_no_response(search_answer) == "yes":
            grounding_context = f" {self.__handle_search(text)} "

        # create previous conversation context
        chat_context = PROMPT
        memory = await self.rd.get(user_id)
        if memory:
            chat_context = f"{chat_context} {memory}"

        # generate response
        response = (
            await self.model.generate_content_async(
                f"{chat_context}{grounding_context} [User]: {text} [Gemini]: ",
                generation_config=genai.GenerationConfig(temperature=0.1),
            )
        ).text

        return response

    def __handle_search(self, query):
        """Performs a google search with the given query"""
        search_result = (
            self.search_service.cse()
            .list(
                q=query,
                cx=self.search_cx,
            )
            .execute()
        )

        # get top 5 search snippets
        grounding_context = f"[System] Search Engine Results: {{"
        for item in search_result["items"][:5]:
            grounding_context += (
                f"{{title: {item['title']}, snippet: {item['snippet']}}}, "
            )
        grounding_context += f"}}"
        return grounding_context

    def __clean_yes_no_response(self, str_in):
        """data cleaning to get a 'yes' or 'no' answer from the chatbot"""
        return (
            str_in.lower().strip().translate(str.maketrans("", "", string.punctuation))
        )
