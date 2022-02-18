import streamlit as st
from api import open_ai
from custom_elements import header_title
from custom_elements import horizontal
from custom_elements import sub_header_title
from custom_elements import text
from custom_elements import text_left
import requests

if "input_data_" not in st.session_state:
    st.session_state.input_data_ = {}

if "tagline_" not in st.session_state:
    st.session_state.tagline_ = []

if "generate_button_state_" not in st.session_state:
    st.session_state.generate_button_state_ = False

if "template_name_dict_" not in st.session_state:
    st.session_state.template_name_dict_ = {}

if "url_list_" not in st.session_state:
    st.session_state.url_list_ = []

unsplash_key = st.secrets["UNSPLASH_KEY"]
switchboard_key = st.secrets["SWITCHBOARD_KEY"]
headers = {'Content-Type': 'application/json','X-API-Key': switchboard_key}

def generate(input_data):
	tag_out = ""
	tag = op.tagline(input_data["description"], input_data["product"])
	tag = tag[0].replace("|", "")
	tag = tag.split(" ")
	for word in tag:
		tag_out += word[0].upper() + word[1:]+ " "

	st.session_state.tagline_ = [tag_out]

	#header = op.header(input_data["description"], input_data["demography"], input_data["intent"], input_data["tone"], input_data["product"])
	# tags = op.hashtag(input_data["description"])
	# st.write(tags)

def get_templates_elements():
	response_template = requests.get('https://api.canvas.switchboard.ai/templates', headers=headers)
	for template in response_template.json()["templates"]:
		api_name = template["apiName"]
		elements = []
		url = 'https://api.canvas.switchboard.ai/template/'+api_name+'/elements'
		response_elements = requests.get(url=url, headers=headers)
		for field_elements in response_elements.json()["fields"]:
			elements.append(field_elements["name"])
		st.session_state.template_name_dict_[api_name] = elements
	#st.write(st.session_state.template_name_dict_)

def generate_data(product, tag, template_name, template_elements):
	data = """{
			"template":\""""+ template_name+"\","+"""
			"sizes": [
			{
				"width": 1920,
				"height": 1080,
				"elements":{"""
	data_end = """}
			}
			]
		}
	"""

	num_tag = 0
	for i in template_elements:
		if i[:-2] == "tag":
			num_tag += 1

	product = "\""+product.upper()+"\""
	tag = "\""+tag+"\""
	for element in template_elements:
		if element[:-2] == "product":
			temp = "\""+element+"\":{\"text\": "+product+"},"
			data += temp
		if element[:-2] == "tag" and num_tag == 1:
			temp = "\""+element+"\":{\"text\": "+tag+"},"
			data += temp
		if element[:-2] == "tag" and num_tag == 2:
			t_split = tag.split()
			t_len = len(t_split)
			t1 = " ".join(t_split[0:int(t_len/2)])+"\""
			t2 = "\""+" ".join(t_split[int(t_len/2):])
			if element[-1] == "1":
				temp = "\""+element+"\":{\"text\": "+t1+"},"
				data += temp
			if element[-1] == "2":
				temp = "\""+element+"\":{\"text\": "+t2+"},"
				data += temp
		if element[:-2] == "img":
			temp = "\""+element+"\":{\"url\": \""+st.session_state.url_list_[0]+"\"},"
			data += temp

	data = data[:-1]+data_end
	#st.write(data)
	return data

def switchboard(product, tag):
	for key,value in st.session_state.template_name_dict_.items():
		data = generate_data(product, tag, key, value)
		response = requests.post('https://api.canvas.switchboard.ai/', headers=headers, data=data)
		with st.container():
			cols = st.columns([1,5,1])
			cols[0].text("")
			cols[2].text("")
			cols[1].image(response.json()["sizes"][0]["url"])
			horizontal(cols[1])

def get_image():
    url_list = []
    topics = op.keywords(st.session_state.input_data_["description"])
    for topic in topics:
        images = requests.get("https://api.unsplash.com/search/photos?query="+topic+"&orientation=landscape&page=1&client_id=" + unsplash_key)
        #print(images)
        data = images.json()
        result = data.get("results")
        if len(result) > 0:
            urls = result[0].get("urls")
            url_list.append(urls.get("regular"))
            print(urls.get("regular"))
        else:
            url_list.append(-1)
    st.session_state.url_list_ = url_list

if __name__ == "__main__":
    
	op = open_ai()
	st.set_page_config(layout="wide")
	header_title("Caption.AI")
	horizontal()
	with st.container():
		cols=st.columns([1,6,0.6])
		cols[2].text("")
		#sub_header_title("Set Goals", cols[0])
		text("Demography", cols[0])
		st.session_state.input_data_["demography"] = cols[1].selectbox(label="", options=("General Audience", "Youth", "Adults", "Children"), key=0)
		text("Intent", cols[0])
		st.session_state.input_data_["intent"] = cols[1].selectbox(label="", options=("Inform", "Describe", "Convince"), key=1)
		text("Tone", cols[0])
		st.session_state.input_data_["tone"] = cols[1].selectbox(label="", options=("Neutral", "Confident", "Joyful", "Optimistic", "Friendly", "Urgent"))
		text("Organization Name", cols[0])
		st.session_state.input_data_["product"] = cols[1].text_input(label="")

		text("Description", cols[0])
		st.session_state.input_data_["description"] = cols[1].text_area(label = "", height = 238)
		cols[1].text("")
		gen_button = cols[1].button(label="Auto Generate")
		if gen_button or st.session_state.generate_button_state_:
			st.session_state.generate_button_state_ = True
			if not st.session_state.tagline_ or gen_button:
				generate(st.session_state.input_data_)
			horizontal()
			header_title("Results")
			if not st.session_state.template_name_dict_:
				get_templates_elements()
			if not st.session_state.url_list_:
				get_image()
			switchboard(st.session_state.input_data_["product"],st.session_state.tagline_[0])
