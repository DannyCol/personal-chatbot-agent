## What is this?
A personalizable website / API to run a voice-activated chatbot using tools from Google/GCP (Gemini, Google TTS/STT, Google Search, Cloud Run, and a GKE cluster). 

Tooling information:
* CI/CD through Github Actions, Docker builds
* Frontend: Typescript + React with Vite
* Backend: Python

## Why?
Being able to control the logic of a chatbot can be prefered rather than using a pre-built agent.
## Future tasks:
* Add a vector database to the GKE cluster for additional contextual information, rather than relying just on the current Redis cache.
* Add a chat interface to show the conversation / images pulled from google search if needed - add logic to the agent to do this.
* Add the configuration for the GKE cluster to the repository/cicd pipeline
## Costs involved?
Everything should run for free within some quota limits, such as a monthly quota on the total minutes of audio processed by the speech services, and 100 google searches a day through the API.

## Documentation
### Run in production
If you wish to run your own version of this chatbot on GCP, you will need to define the following repository secrets for the CI/CD pipeline to work:

* `GCP_CHAT_PROJECT_ID` : self-explanatory 
* `GCP_CHAT_REGION` : the region of the GKE cluster and Cloud Run service. Pick the closest one to you.
* `GCP_CHAT_ZONE` : the zone where the Cloud Run service will run.
* `GCP_CHAT_CR_SERVICE_NAME` : your desired cloud run service name, and artifact repository name
* `GCP_SA_KEY` : GCP service account key, as JSON for deployment through github actions. Alternative authentication methods exist.
* `GCP_CR_SA_EMAIL_PREFIX` : GCP service account email name prefix that the Cloud Run service will use
* `firebaseConfig_ts` : text for a file that simply defines the firebase config object: `export const firebaseConfig = {...}`. You may want to keep this private, which is why I defined the text of the file as a github secret.
* `GCP_CHAT_SECRETS_ID` : id of the secret in GCP's Secret Manager
    * The value of the secret needs to be a JSON object / dictionary with the following keys:
        * `GEN_AI_API_KEY` : Gemini API developer key
        * `GOOGLE_SEARCH_API_KEY` : Custom Search API key
        * `GOOGLE_SEARCH_ENGINE_ID` : Custom Search search engine id (you must create a custom search engine - just the API part though)
* `GCP_GKE_REDIS_NODEPORT` : a port for the redis service on a GKE cluster, will add info for this later.

