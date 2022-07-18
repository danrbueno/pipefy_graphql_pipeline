# -*- coding: utf-8 -*-
"""config.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1txQekafm-zh67gl4FNNpsoFKWvQP7eUq
"""

# Global variables for this project

# GraphQL API URL
API_URL      = "https://api.pipefy.com/graphql"

# User token to access Pipefy.
# You can get this token accessing your account preferences on Pipefy, by:
# - visit https://app.pipefy.com/ 
# - log in to your Pipefy account
# - go to https://app.pipefy.com/tokens
PIPEFY_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9."
PIPEFY_TOKEN += "eyJ1c2VyIjp7ImlkIjozMDIxMTc5NjcsImVtYWlsIjoiYnVlbm8xOTgyQGdtYWlsLmNvbSIsImFwcGxpY2F0aW9uIjozMDAxNzc0OTd9fQ."
PIPEFY_TOKEN += "HlsNAqBXybu22zYagw5QumOpiEMXt8YFZWO8q3abJ62LJzWzWUVqnBYETdqAutz81iwIIhfoBiXVO2i6g-sGjQ"

# JSON heders
ACCEPT       = "application/json"
CONTENT_TYPE = "application/json"

# Your pipe id (https://app.pipefy.com/pipes/<PIPE_ID>)
PIPE_ID      = "302551116"

# The fields of the Pipefy cards you want to extract from GraphQL
EDGES        = "{ edges"
EDGES       += " { node"
EDGES       += " { id title assignees { id } comments { text } comments_count"
EDGES       += " current_phase { name } done due_date fields { name value } labels { name }"
EDGES       += " phases_history { phase { name } firstTimeIn lastTimeOut } url } } pageInfo { endCursor startCursor hasNextPage } }"
