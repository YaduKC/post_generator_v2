import openai
import requests
from PIL import Image
import io
import streamlit as st

class open_ai:

    def __init__(self):
        openai.api_key = st.secrets["OPENAI_KEY"]

    def product_description(self, description, name, num_responses=1):
        desc = []
        for i in range(num_responses):
            response = openai.Completion.create(
                engine="davinci-instruct-beta-v3",
                prompt="Write a fake marketting for a product called \""+name+"\" \n\""+description+"\".",
                temperature=1.0,
                max_tokens=200,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            desc.append(response.choices[0].get("text").strip("\n"))
        return desc

    def tagline(self, description, name, num_responses=1):
        taglines = []
        for i in range(num_responses):
            response = openai.Completion.create(
              engine="davinci-instruct-beta-v3",
              prompt="Write a short creative tagline for the business named \"" + name + "\" using the description given below.\n\""+description+"\"",
              temperature=1,
              max_tokens=64,
              top_p=1,
              frequency_penalty=0,
              presence_penalty=0
            )
            taglines.append((response.choices[0].get("text").strip("\n")).replace("\"","").replace(".",""))
        return taglines

    def hashtag(self, description, num_responses=1):
        hashtags = []
        for i in range(num_responses):
            response = openai.Completion.create(
              engine="davinci-instruct-beta-v3",
              prompt="Write 10 hashtags for social media using the description given below.\n\""+description+"\"",
              temperature=0.7,
              max_tokens=64,
              top_p=1,
              frequency_penalty=0,
              presence_penalty=0
            )
            hashtags.append(response.choices[0].get("text").strip("\n"))
        return hashtags

    def keywords(self, description):
        response = openai.Completion.create(
        engine="davinci-instruct-beta-v3",
        prompt="Text: " + description + "\n\nMain Keyword is:",
        temperature=0.3,
        max_tokens=80,
        top_p=1.0,
        frequency_penalty=0.8,
        presence_penalty=0.0,
        stop=["\n"]
        )
        key = response.choices[0].get("text")
        return list(set(key.split()))

    def header(self, description, demography, intent, tone, name):

        if intent[0] == "Convince": intent = "convincing"
        elif intent[0] == "Inform": intent = "informative"
        elif intent[0] == "Describe": intent = "descriptive"

        response = openai.Completion.create(
          engine="davinci-instruct-beta-v3",
          prompt="Write a 60 word"+ intent +" advertisement for "+ demography[0] +" with an "+ tone[0] +" tone using the description given below for the business named \"" + name + "\".\n\""+description+"\"",
          temperature=0.7,
          max_tokens=100,
          top_p=1,
          frequency_penalty=0,
          presence_penalty=0
        )
        return "\"" + response.choices[0].get("text").strip("\n") + "\""





