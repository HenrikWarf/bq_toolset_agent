import os

from google.adk.agents.llm_agent import LlmAgent
from google.adk.auth.auth_credential import AuthCredentialTypes
from google.adk.tools.bigquery.bigquery_credentials import BigQueryCredentialsConfig
from google.adk.tools.bigquery.bigquery_toolset import BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig
from google.adk.tools.bigquery.config import WriteMode
import google.auth

# Define an appropriate credential type
# Using APPLICATION_DEFAULT for local development with gcloud auth
#CREDENTIALS_TYPE = "APPLICATION_DEFAULT"
CREDENTIALS_TYPE = AuthCredentialTypes.SERVICE_ACCOUNT
if CREDENTIALS_TYPE == AuthCredentialTypes.SERVICE_ACCOUNT:
  # Initialize the tools to use the credentials in the service account key.
  # If this flow is enabled, make sure to replace the file path with your own
  # service account key file
  # https://cloud.google.com/iam/docs/service-account-creds#user-managed-keys
  creds, _ = google.auth.load_credentials_from_file("/Users/henrikw/Documents/bq_analytics/bq_toolset/sa/ml-developer-project-fe07-5f1df724f1b5.json")
  credentials = BigQueryCredentialsConfig(credentials=creds)


# Define an appropriate application name
BIGQUERY_AGENT_NAME = "adk_sample_bigquery_agent"

# Vertex AI project/region (used for fully-qualified Gemini model path)
# Falls back to gcloud-configured project/region if env vars are unset
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "ml-developer-project-fe07")
REGION = os.getenv("GOOGLE_CLOUD_REGION", os.getenv("VERTEX_AI_REGION", "us-central1"))

# Define BigQuery tool config with write mode set to allowed. Note that this is
# only to demonstrate the full capability of the BigQuery tools. In production
# you may want to change to BLOCKED (default write mode, effectively makes the
# tool read-only) or PROTECTED (only allows writes in the anonymous dataset of a
# BigQuery session) write mode.
tool_config = BigQueryToolConfig(
    write_mode=WriteMode.BLOCKED, 
    #application_name=BIGQUERY_AGENT_NAME,
    # Optionally specify project here if not set via gcloud
    #project="ml-developer-project-fe07"
)

bigquery_toolset = BigQueryToolset(
    credentials_config=credentials, bigquery_tool_config=tool_config
)

# The variable name `root_agent` determines what your root agent is for the
# debug CLI
root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name=BIGQUERY_AGENT_NAME,
    description=(
        "Agent to answer questions about BigQuery data and models and execute"
        "SQL queries."
    ),
    instruction="""\
        You are a data science agent with access to several BigQuery tools.
        Make use of those tools to answer the user's questions.
        Use the appropriate tools to retrieve BigQuery metadata and execute SQL queries in order to answer the users question.
       
        Run these queries in the project-id: ml-developer-project-fe07.
        ALL questions relate to data stored in the customer_data_retail dataset.
        ALL questions relate to data stored in the customers table.
    """,
    tools=[bigquery_toolset],
)