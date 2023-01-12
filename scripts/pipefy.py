import json
import requests
import pandas as pd
from unidecode import unidecode
import os

class Pipe(object):
    
    def __init__(self, pipe_id):
        # GraphQL API URL
        self._api_url = "https://api.pipefy.com/graphql"

        # JSON heders
        self._accept       = "application/json"
        self._content_type = "application/json"

        # Your pipe id (https://app.pipefy.com/pipes/<PIPE_ID>)
        self._pipe_id      = pipe_id

        # The fields of the Pipefy cards you want to extract from GraphQL
        # Reference: https://api-docs.pipefy.com/reference/objects/Card/
        self._edges = "{ edges"
        self._edges += " { node"
        self._edges += " { id title comments_count done due_date url current_phase { id name }"
        self._edges += " assignees { id name } comments { id text } labels { id name }"
        self._edges += " phases_history { phase { id name } firstTimeIn lastTimeOut } fields { name value } } }"
        self._edges += " pageInfo { endCursor startCursor hasNextPage } }"
    
    
    # graphql
    def get_json_response(self, page_info = {}) :
        if page_info:
            param_after = ", after: \"%(start_cursor)s\"" % {"start_cursor": page_info["endCursor"]}
        else:
            param_after = ""
            
        # User token to access Pipefy.
        # You can get this token accessing your account preferences on Pipefy, by:
        # - visit https://app.pipefy.com/ 
        # - log in to your Pipefy account
        # - go to https://app.pipefy.com/tokens
        # - save the token in a JSON file like this:
        # { "token": "Bearer <YOUR TOKEN HERE>" }
        basePath = os.path.dirname(os.path.abspath(__file__))
        token_file = pd.read_json(basePath + "/token.json", typ="series")
        token = token_file.token                

        # headers
        headers = {
                    "Accept": self._accept,
                    "Content-Type": self._content_type,
                    "Authorization": token
                    }

        # Pipefy limits 50 cards per page in query
        self._query = "{ allCards(pipeId: %(pipe_id)s, first: 50%(param_after)s) %(edges)s }" % {"pipe_id"    : self._pipe_id, 
                                                                                            "param_after": param_after, 
                                                                                            "edges"      : self._edges}

        json_query = {"query": self._query}

        # response
        response = requests.request("POST", url = self._api_url, json = json_query, headers = headers)

        # json response
        json_data = json.loads(response.text)
        
        return json_data
    
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

    # Load a dynamic list of dataframes with the Pipefy cards
    # Normalize the data found in the main dataframe, breaking in new dataframes with the card_id reference.
    def set_dataframes(self, data):                
        df_cards = pd.DataFrame()
        dfs     = {}

        # list of sub-dataframes that will be as lists or dicts in the main dataframe
        sub_dfs = [{"name":"current_phase", "type":"dict"},
                    {"name":"assignees", "type":"list"},
                    {"name":"comments", "type":"list"},
                    {"name":"labels", "type":"list"},
                    {"name":"phases_history", "type":"list"},
                    {"name":"fields", "type":"list"}]
        
        # loop to get all the cards and put into the dataframe
        for i in range(len(data)):
            node = data[i]["node"]
            row_pipe = {}            
            
            # loop to get all the attributes in the cards. To see all the attributes, see self._edges
            for attribute in node:                                   
                row_pipe[attribute] = node[attribute]                
            
            df_cards_row = pd.DataFrame([row_pipe])            
            df_cards = pd.concat([df_cards, df_cards_row], ignore_index=True)
        
        df_cards = df_cards.fillna(value="")
        df_cards.rename(columns={'id': 'card_id'}, inplace = True)          
        
        # load the sub-dataframes identified with dicts or lists in the main dataframe
        for item in sub_dfs:
            if (item["type"] == "dict"):
                sub_df = pd.concat([df_cards['card_id'], df_cards[item["name"]].apply(pd.Series)], axis=1)                        
            
            elif (item["type"] == "list"):
                sub_df = pd.concat([df_cards['card_id'], df_cards[item["name"]]], axis=1)
                sub_df = sub_df.explode(item["name"], ignore_index=True).dropna()
                sub_df = pd.concat([sub_df['card_id'], sub_df[item["name"]].apply(pd.Series)], axis=1)

            sub_df = sub_df.fillna(value="")
            dfs["df_"+item["name"]] = sub_df            
            df_cards = df_cards.drop(columns=[item["name"]])
            
        dfs["df_cards"] = df_cards
            
        return dfs