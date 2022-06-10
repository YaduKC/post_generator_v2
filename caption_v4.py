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

if "header_" not in st.session_state:
    st.session_state.header_ = []

if "hashtags_" not in st.session_state:
    st.session_state.hashtags_ = []

if "template_name_dict_" not in st.session_state:
    st.session_state.template_name_dict_ = {}

if "url_list_" not in st.session_state:
    st.session_state.url_list_ = []

if "image_index_" not in st.session_state:
    st.session_state.image_index_ = -1
	
if "accept_tag_" not in st.session_state:
    st.session_state.accept_tag_ = False

if "accept_header_" not in st.session_state:
    st.session_state.accept_header_ = False

if "accept_hashtags_" not in st.session_state:
    st.session_state.accept_hashtags_ = False

unsplash_key = st.secrets["UNSPLASH_KEY"]
switchboard_key = st.secrets["SWITCHBOARD_KEY"]
headers = {'Content-Type': 'application/json','X-API-Key': switchboard_key}

def generate(input_data):
	tag_out = ""
	tag = op.tagline(input_data["description"], input_data["product"])
	tag = tag[0].replace("|", "")
	tag = tag.split(" ")
	if len(tag)>0:
		for word in tag:
			tag_out += word[0].upper() + word[1:]+ " "

		st.session_state.tagline_ = [tag_out]
	else:
		st.session_state.tagline_ = ["Missing"]

	
	st.session_state.hashtags_ = op.hashtag(input_data["description"])
	# st.write(tags)

def generate_header(input_data):
	st.session_state.header_ = op.header(input_data["description"], input_data["demography"], input_data["intent"], input_data["tone"], input_data["product"])

def generate_hashtags(input_data):
	st.session_state.hashtags_ = op.hashtag(input_data["description"])

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

	if template_name[-1] == "v":
		data = """{
				"template":\""""+ template_name+"\","+"""
				"sizes": [
				{
					"width": 1080,
					"height": 1080,
					"elements":{"""
		data_end = """}
				}
				]
			}
		"""
	else:
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
			temp = "\""+element+"\":{\"url\": \""+st.session_state.url_list_[st.session_state.image_index_]+"\"},"
			data += temp

	data = data[:-1]+data_end
	#st.write(data)
	return data

def switchboard(product, tag):
	for key,value in st.session_state.template_name_dict_.items():
		with st.spinner("Processing Templates..."):
			data = generate_data(product, tag, key, value)
			response = requests.post('https://api.canvas.switchboard.ai/', headers=headers, data=data)
			with st.container():
				if key[-1] == "v":
					cols = st.columns([1,1,1])
				else:
					cols = st.columns([1,5,1])
				cols[0].text("")
				cols[2].text("")
				#st.write(response.json())
				cols[1].image(response.json()["sizes"][0]["url"])
				horizontal(cols[1])

def get_image(color=""):
	url_list = []
	topics = op.keywords(st.session_state.input_data_["description"])
	for topic in topics:
		if len(topic)>3:
			topic=topic.replace(",","")
			#st.write(topic)
			images = requests.get("https://api.unsplash.com/search/photos?query="+topic+"&page=1&client_id=" + unsplash_key)
			#print(images)
			data = images.json()
			result = data.get("results")
			count = 0
			if len(result) > 0:
				for u in result:
					url_list.append(u["urls"]["regular"])
					count += 1
					if count>=4:
						break
	#st.write(url_list)
	st.session_state.url_list_ = url_list

def reset():
	st.session_state.input_data_ = {}
	st.session_state.tagline_ = []
	st.session_state.template_name_dict_ = {}
	st.session_state.url_list_ = []
	st.session_state.header_ = []
	st.session_state.hashtags_ = []
	st.session_state.accept_tag_ = False
	st.session_state.accept_header_ = False
	st.session_state.accept_hashtags_ = False
	st.experimental_rerun()

if __name__ == "__main__":
    
	op = open_ai()
	st.set_page_config(layout="wide")
	header_title("Caption.AI")
	horizontal()
	regen_tagline = False
	regen_header = False
	regen_hashtags = False
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
		text("Organization/Product Name", cols[0])
		st.session_state.input_data_["product"] = cols[1].text_input(label="")

		text("Description", cols[0])
		st.session_state.input_data_["description"] = cols[1].text_area(label = "", height = 238)
		cols[1].text("")
		gen_button = cols[1].button(label="Generate")
		next_ = False
		accept = False
		reset_ = False
		if gen_button or st.session_state.tagline_:
			if st.session_state.input_data_["product"] == "" or st.session_state.input_data_["description"] == "":
				st.error("Enter Details")
			else:
				with st.spinner("Generating Tagline..."):
					if not st.session_state.tagline_:
						generate(st.session_state.input_data_)
						generate_header(st.session_state.input_data_)
						generate_hashtags(st.session_state.input_data_)

					horizontal()
					with st.container():
						cols = st.columns([5,1])
						cols[0].subheader("Tagline:")
						cols[0].info(st.session_state.tagline_[0])
						cols[1].header("")
						cols[1].header("")
						regen_tagline = cols[1].button(label="Regenerate", key=9)
					with st.container():
						cols = st.columns([5,1])
						cols[0].subheader("Header:")
						cols[0].info(st.session_state.header_)
						cols[1].header("")
						cols[1].header("")
						regen_header = cols[1].button(label="Regenerate", key=24)
					with st.container():
						cols = st.columns([5,1])
						cols[0].subheader("Hashtags:")
						cols[0].info(st.session_state.hashtags_[0])
						cols[1].header("")
						cols[1].header("")
						regen_hashtags = cols[1].button(label="Regenerate", key=34)
					horizontal()
					with st.container():
						cols = st.columns([1,1,1,8])
						cols[3].text("")
						accept = cols[0].button(label="Accept")
						reset_ = cols[1].button(label="Reset")
		horizontal()
		if reset_:
			reset()
		if regen_tagline:
			with st.spinner("Generating Tagline..."):
				generate(st.session_state.input_data_)
			st.experimental_rerun()
		if regen_header:
			with st.spinner("Generating Header..."):
				generate_header(st.session_state.input_data_)
			st.experimental_rerun()
		if regen_hashtags:
			with st.spinner("Generating Hashtags..."):
				generate_hashtags(st.session_state.input_data_)
			st.experimental_rerun()
			
		"""if accept or st.session_state.accept_tag_:
			st.session_state.accept_tag_ = True
			#header_title("Results")
			if not st.session_state.template_name_dict_:
				with st.spinner("Retrieving Templates..."):
					get_templates_elements()
			if not st.session_state.url_list_:
				with st.spinner("Retrieving Template Images..."):
					get_image()
			st.subheader("Select Image")
			cols = st.columns([1,1,1])
			col = 0
			for count, image in enumerate(st.session_state.url_list_):
				col = count%3
				with cols[col].expander(label="Image", expanded=True):
					st.image(image)
					if st.button(label="Accept", key=count):
						st.session_state.image_index_ = count
			horizontal()
			if st.session_state.image_index_ != -1:
				header_title("Results")
				switchboard(st.session_state.input_data_["product"],st.session_state.tagline_[0])"""
