# packages

import config
import json
import requests
import pandas as pd
from unidecode import unidecode

# graphql
def get_json_response(page_info = {}) :

  if page_info:
    param_after = ", after: \"%(start_cursor)s\"" % {"start_cursor": page_info["endCursor"]}
  else:
    param_after = ""

  # headers
  headers = {
      "Accept": config.ACCEPT,
      "Content-Type": config.CONTENT_TYPE,
      "Authorization": "Bearer %s" % config.PIPEFY_TOKEN
  }

  # Pipefy limits 50 cards per page in query
  query = "{ allCards(pipeId: %(pipe_id)s, first: 50%(param_after)s) %(edges)s }" % {"pipe_id"    : config.PIPE_ID, 
                                                                                     "param_after": param_after, 
                                                                                     "edges"      : config.EDGES}
  json_query = {"query": query}
  
  # response
  response = requests.request("POST", url = config.API_URL, json = json_query, headers = headers)

  # json response
  json_data = json.loads(response.text)

  return json_data

def get_cards():
  json_response = get_json_response()
  cards = json_response["data"]["allCards"]["edges"]
  page_info = json_response["data"]["allCards"]["pageInfo"]

  while page_info["hasNextPage"] == True:
    json_response = get_json_response(page_info)
    last_cards = json_response["data"]["allCards"]["edges"]
    cards += last_cards
    page_info = json_response["data"]["allCards"]["pageInfo"]

  return cards

# Load a dynamic dataframe with the Pipefy cards
def load_dataframe(cards):
  df = pd.DataFrame()
  cards = get_cards()

  # loop to get all the cards and put into the dataframe
  for i in range(len(cards)):
    node = cards[i]["node"]
    row = {}

    # loop to get all the attributes in the cards. To see all the attributes, open config.py and see the string EDGES
    for attribute in node:

      # if the attribute is not a list and not a dict, we just set the dataset column with the attribute value
      if (isinstance(node[attribute], list) == False) and (isinstance(node[attribute], dict) == False):
        row[attribute] = node[attribute]

      # if we have a dict in the attribute, we have to get all the values and join with a '|' to the column
      elif isinstance(node[attribute], dict):
        arr_values = []
        for key in node[attribute]:
          arr_values.append(node[attribute][key])
        row[attribute] = " | ".join(arr_values)

      # if we have a list in the attribute, we have to get all the values and join with a '|' and a '\n\n' in the end of each item to the column
      elif isinstance(node[attribute], list):
        arr_dict = []

        for item in range(len(node[attribute])):
          arr_values = []

          for key in node[attribute][item]:
            arr_values.append(str(node[attribute][item][key]))

          arr_dict.append(" | ".join(arr_values))

        row[attribute] = "\n\n".join(arr_dict)
      
      # Get all the customized fields from the pipe
      if(attribute == 'fields'):
        for field in range(len(node[attribute])):
          field_name = unidecode(node[attribute][field]["name"].lower().replace(" ","_"))
          row[field_name] = node[attribute][field]["value"]

      # Get all the pahses history from the pipe
      if(attribute == 'phases_history'):
        for phase in range(len(node[attribute])):
          phase_name = unidecode(node[attribute][phase]["phase"]["name"].lower().replace(" ","_"))
          row[phase_name+"_first_time_in"] = node[attribute][phase]["firstTimeIn"]
          row[phase_name+"_last_time_out"] = node[attribute][phase]["lastTimeOut"]
    
    df = df.append(row, ignore_index=True)
    df = df.fillna(value="")
  return df

