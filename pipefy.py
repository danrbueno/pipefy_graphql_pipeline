#!/usr/bin/env python
# coding: utf-8

# In[33]:


# packages

import json
import requests
import pandas as pd
from unidecode import unidecode


# In[126]:


class Pipe(object):
    
    def __init__(self, pipe_id):
        # GraphQL API URL
        self._api_url = "https://api.pipefy.com/graphql"

        # User token to access Pipefy.
        # You can get this token accessing your account preferences on Pipefy, by:
        # - visit https://app.pipefy.com/ 
        # - log in to your Pipefy account
        # - go to https://app.pipefy.com/tokens
        self._token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9."
        self._token += "eyJ1c2VyIjp7ImlkIjozMDIxMTc5NjcsImVtYWlsIjoiYnVlbm8xOTgyQGdtYWlsLmNvbSIsImFwcGxpY2F0aW9uIjozMDAxNzc0OTd9fQ."
        self._token += "HlsNAqBXybu22zYagw5QumOpiEMXt8YFZWO8q3abJ62LJzWzWUVqnBYETdqAutz81iwIIhfoBiXVO2i6g-sGjQ"

        # JSON heders
        self._accept       = "application/json"
        self._content_type = "application/json"

        # Your pipe id (https://app.pipefy.com/pipes/<PIPE_ID>)
        self._pipe_id      = pipe_id #"302551116"

        # The fields of the Pipefy cards you want to extract from GraphQL
        self._edges        = "{ edges"
        self._edges       += " { node"
        self._edges       += " { id title assignees { id } comments { text } comments_count"
        self._edges       += " current_phase { id name } done due_date fields { name value } labels { name }"
        self._edges       += " phases_history { phase { name } firstTimeIn lastTimeOut } url } } pageInfo { endCursor startCursor hasNextPage } }"
    
    
    # graphql
    def get_json_response(self, page_info = {}) :
        try:
            if page_info:
                param_after = ", after: \"%(start_cursor)s\"" % {"start_cursor": page_info["endCursor"]}
            else:
                param_after = ""

            # headers
            headers = {
                        "Accept": self._accept,
                        "Content-Type": self._content_type,
                        "Authorization": "Bearer %s" % self._token
                        }

            # Pipefy limits 50 cards per page in query
            query = "{ allCards(pipeId: %(pipe_id)s, first: 50%(param_after)s) %(edges)s }" % {"pipe_id"    : self._pipe_id, 
                                                                                               "param_after": param_after, 
                                                                                               "edges"      : self._edges}

            json_query = {"query": query}

            # response
            response = requests.request("POST", url = self._api_url, json = json_query, headers = headers)

            # json response
            json_data = json.loads(response.text)
            
            return json_data
        
        except Exception as error:
            print("Error: " + error)        
    
    def get_data(self):
        json_response = self.get_json_response()
        cards = json_response["data"]["allCards"]["edges"]
        page_info = json_response["data"]["allCards"]["pageInfo"]

        while page_info["hasNextPage"] == True:
            json_response = self.get_json_response(page_info)
            last_cards = json_response["data"]["allCards"]["edges"]
            cards += last_cards
            page_info = json_response["data"]["allCards"]["pageInfo"]

        return cards

    # Load a dynamic dataframe with the Pipefy cards
    def load_dataframe(self, data):
        df = pd.DataFrame()

        # loop to get all the cards and put into the dataframe
        for i in range(len(data)):
            node = data[i]["node"]
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

            df_row = pd.DataFrame([row])
            df = pd.concat([df, df_row], ignore_index=True)
            df = df.fillna(value="")
        
        return df

