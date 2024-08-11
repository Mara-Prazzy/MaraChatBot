
import streamlit as st
from streamlit import session_state as ssv
import streamlit_authenticator as stauth

from streamlit_extras.stylable_container import stylable_container
from dotenv import load_dotenv
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai.chat_models import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores import Chroma
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
import pandas as pd
#from htmlTemplates3_Summit import css, bot_template, user_template
from htmlTemplateAltInno_page import pagecss
from htmlTemplateAltInno_chat import csschat, bot_template, user_template
from htmTemplateAltInno_scroll import script_col_noscroll, script_col_scroll, script_col_active
from chat_literals import *
from email_literals import *
from chat_params import *
from vs_literals import *
from streamlit_cognito_userpool import *

import time
import os
import glob
import yaml

CSS_MESSAGE_REPLACE = "{{MSG}}"

filename_vectorstore_Pivot = "VectorStore/FAISS_VS_YC_GenZ_OAI_Pivot"
filename_vectorstore_Article = "VectorStore/FAISS_VS_YC_GenZ_OAI_Article99"
filename_vectorstore_Reddit = "VectorStore/FAISS_VS_YC_GenZ_OAI_Reddit100"
filename_vectorstore_Matrix = "VectorStore/231122_YCMatrix_VS"
filename_matrix_docs = "Input/231123_Matrix_XRef_csv.csv"
filebase_doc_vectorstore = "ContentVS/"

PIVOT_VS = "Covid interviews"
PIVOT_DESC = "18,000 interview transcripts about GenZ & Covid"
ARTICLE_VS = "Articles"
ARTICLE_DESC = "100 news articles and reports from 2022-23 on GenZ"
REDDIT_VS = "Reddit opinions"
REDDIT_DESC = "Top 100 Reddit topics on GenZ (with 41,000 comments)"
MATRIX_VS = "YC-curated"
MATRIX_DESC = "Selected GenZ articles & reports by the Youthful Cities team"

KEY_VSRADIO = "VSRadio"
KEY_CREATESLIDER = "CreateSlider"

WDGT_VS = "widget_vectorstore"
WDGT_VS_INIT = PIVOT_VS
WDGT_VS_FAKESTART = ARTICLE_VS
WDGT_VS_CUR	= WDGT_VS_FAKESTART   #To trigger loading on first time
WDGT_VSDOC = "widget_docvs"
WDGT_VSDOC_INIT = False
WDGT_VSDOC_CUR = WDGT_VSDOC_INIT
WDGT_SOURCES = "widget_sources"
WDGT_SOURCES_INIT = True
WDGT_SOURCES_CUR = WDGT_SOURCES_INIT
WDGT_CREATIVITY = "widget_creativity"
WDGT_CREATIVITY_INIT = 6
WDGT_CREATIVITY_CUR = WDGT_CREATIVITY_INIT
WDGT_EMAIL_NAME = "widget_email_name"
WDGT_DOCNUM = "widget_doc_num"

CHAT_PROMPT_STRING = "Ask a question:"
INIT_VAL_CHAT_INPUT = None
SS_CHAT_WDGT_INPUT = "chat_wdgt_input"
SS_CUR_CHAT_INPUT = "cur_chat_input"

KEY_YCNNNNN = "yc_key"
KEY_REFID = "ref_id"
KEY_TITLE = "title"
KEY_LINK = "link"
KEY_SUMMARY = "summary"
KEY_FILENAME = "file_name"
KEY_COLLECTION = "collection"

filename_save_root = "Conversations/"
filename_logfile = filename_save_root + "Log_YC_ChatDemo.txt"

title_string = "Chat about Gen Z"
prompt_string = "Ask a question"
user_avatar = "images/person_blue_sq.png"
robot_avatar = "images/robot_orange.png"

TAB_0 = ""
TAB_1 = "   "
TAB_2 = "      "
TAB_3 = "         "

disclaimer = "Now that you’re signed in, the sponsor and developer companies of this chat application \
	(Youthful Cities and Thoughtful Ideation, respectively) would like to remind you that:\n\n"
disclaimer += ("- Although you might find this an excellent and helpful tool, you can’t share your \
	username and password or provide access to anyone without their explicit permission. \
			They can revoke access to any user at any time at their sole discretion.\n\n")
disclaimer += "- This is a prototype, so they don't warrant anything, and they are not liable in any \
			way for its use. Be responsible in using it, and please don’t fault them if something \
			doesn’t work as expected or what you use it for.\n\n"
disclaimer += "- They own any data related to this application, including any chats that you \
			might have. The original documents, reports and articles are owned by the \
			originating authors as per copyright.\n\n"
disclaimer += "- The developer retains all rights and ownership of this application \
			and the software, including the general concept as implemented.\n\n"
disclaimer += "Given these simple rules, enjoy exploring how you can find answers to \
			some of your questions about Youth.\n"

#***********************
#
# Load access keys
#
#***********************

load_dotenv()


#***********************
#
# Security
#
#***********************

filedir_users = "Security/Users/"
filename_default_cookie = "Security/default_login_cookie_summit.yaml"

def login():
	username = st.text_input('Username')
	password = st.text_input('Password', type='password')
	#if st.session_state["authentication_status"]:
	#st.session_state["authentication_status"] = False
	if st.button('Login'):
		try:
			id_token = authenticate_user(username, password)
			#if st.session_state["
			if id_token:
				st.session_state['logged_in'] = True
				st.success('Login successful')
			else:
				st.error("Invalid username or password")	
			#if st.session_state["authentication_status"]:
			#st.write("Authetication status within if loop:", st.session_state["authetication_status"])
			#st.write('ID Token:', id_token)
		except Exception as e:
			st.error(f'Login failed: {e}')
		
	return True


def security_reset_user_file( userid, password, flag_1st):
	filename_yaml_user = filedir_users + userid + ".yaml"
	with open(filename_yaml_user, 'r') as file:
		user_data = yaml.safe_load(file)
		user_data["userinfo"][userid]["password"] = password
		user_data["flag_1st"] = flag_1st
	with open(filename_yaml_user, "w") as file:
		yaml.dump(user_data, file, default_flow_style=False)
	return

def security_allowed_entry():
	entry_ok = False
	if st.session_state["authentication_status"] and st.session_state["Not_1st_time"]:
		entry_ok = True
	return entry_ok

def security_setup():

	#***build up the user dictionary for the login credentials
	users_list = {}
	st.session_state.flags_1st_list = {}
	for user_file in glob.glob(filedir_users + "*.*"):
		with open(user_file, 'r') as file:
			#build up the credential list of users
			user_data = yaml.safe_load(file)
			userinfo = user_data["userinfo"]
			users_list.update(userinfo)
			#build up the dictionary of 1st time flags
			keyslist = list(userinfo)
			username = keyslist[0]
			st.session_state.flags_1st_list[username] = user_data["flag_1st"]

	#print(st.session_state.flags_1st_list)
	st.session_state.credentials_dict = {}
	st.session_state.credentials_dict["usernames"] = users_list
	#print("Cred before: ", st.session_state.credentials_dict)

	#***load the default cookie
	with open(filename_default_cookie, 'r') as file:
		cookie_data = yaml.safe_load(file)
	#print(cookie_data)

	#wait = input("...waiting after builds")

	st.session_state.login_auth = stauth.Authenticate(
		st.session_state.credentials_dict,
		cookie_data['cookie']['name'],
		cookie_data['cookie']['key'],
		cookie_data['cookie']['expiry_days']
	)

	st.session_state["Not_1st_time"] = False

	return

def security_login():

	st.session_state.login_auth.login()
	if st.session_state["authentication_status"]:
		#print("Login Good!")
		#print(st.session_state["username"])
		if st.session_state.flags_1st_list[st.session_state["username"]]:
			#print("Need to request change of password")
			#append_LogFile("1st-time signin --> still needs password changed")
			try:
				if st.session_state.login_auth.reset_password(st.session_state["username"],
				                    fields={'Form name' : 'First Time User - Reset Password:'}):
					st.success('Password modified successfully')
					userid = st.session_state["username"]
					st.session_state.flags_1st_list[userid] = False
					#print("Cred after: ", st.session_state.credentials_dict)
					security_reset_user_file( userid,
					                 st.session_state.credentials_dict["usernames"][userid]['password'],
					                 st.session_state.flags_1st_list[userid])
					st.session_state["Not_1st_time"] = True
					append_LogFile("1st-time signin password changed")
					time.sleep(3)
					st.rerun()
			except Exception \
					as e:
				st.error(e)
				#st.error("Not Reset - Try Again")
		else:
			#print("not a first time user")
			st.session_state["Not_1st_time"] = True
			append_LogFile("Signin")
	elif st.session_state["authentication_status"] is False:
		st.error("Username or password is incorrect")
	elif st.session_state["authentication_status"] is None:
		st.warning("Please enter your username and password")

	return

#***********************
#
# Chat Display and Memory
#
#***********************

def handle_userinput(user_question):
	# get the response to the question
	try:
		response = st.session_state.conversation.invoke({CHAT_QUESTION: user_question})
		source_info = get_source_info(response[CHAT_SOURCE], SOURCE_CLIP)
		append_ExplainSources(response[CHAT_SOURCE])
	except Exception as e:
		error_msg = "Sorry, there seems to be an issue with your question. It is likely" + \
			" that the server is down to find your answer. Please try again with a slightly different " + \
			" question, or you might even have to try later when the server comes up again."
		response = { CHAT_QUESTION : user_question, CHAT_ANSWER : error_msg}
		source_info = " { System Down } "
	# save all the elements of the response
	append_ChatResponse(response[CHAT_QUESTION], response[CHAT_ANSWER])
	append_ChatSources(source_info)
	append_ChatDisplay(response[CHAT_QUESTION], response[CHAT_ANSWER], source_info)
	return

def display_Chat():
	for dispmessage in st.session_state.display_chat:
		with st.chat_message(CHAT_USER, avatar=user_avatar):
			st.write(user_template.replace(CSS_MESSAGE_REPLACE, dispmessage[CHAT_QUESTION]), unsafe_allow_html=True)
		with st.chat_message(CHAT_ASSISTANT, avatar=robot_avatar):
			chat_resp = dispmessage[CHAT_ANSWER]
			if st.session_state[WDGT_SOURCES]:
				chat_resp += "\n\n\n\nSources: " + dispmessage[CHAT_SOURCE]
				#print(chat_resp)
			st.write(bot_template.replace(CSS_MESSAGE_REPLACE, chat_resp), unsafe_allow_html=True)
	return

def get_text():
	input_text = st.text_input("You: ", "", key=CHAT_INPUT)
	return input_text

def clear_chat_mem_hist():
	st.session_state.memory = None
	st.session_state.display_chat = []
	return

def append_ChatDisplay(question, answer, source):
	dict = {}
	dict[CHAT_QUESTION] = question
	dict[CHAT_ANSWER] = answer
	dict[CHAT_SOURCE] = source
	st.session_state.display_chat.append(dict)
	return

#***********************
#
# Sources display added to chat
#
#***********************

def check_if_sources( doc_list):
	doc = doc_list[0]
	src = doc.metadata.get("source")
	src_exist = True
	if src == None:
		src_exist = False
	return src_exist

def source_pattern(str_long):
	#want to extract the PPNNNNNNN-x-y document id from the filename string by ignoring the leading directory
	dirend = str_long.find("/") + 1
	str_short = str_long[dirend:]
	str_short = str_short[:SOURCES_HEADER_USE_LEN]
	return str_short

def get_source_info( doc_list, src_type):
	src_info = ""
	if check_if_sources( doc_list) == False:
		if st.session_state[WDGT_VS_CUR] == PIVOT_VS:
			src_info = "Covid interviews"
		elif st.session_state[WDGT_VS_CUR] == ARTICLE_VS:
			src_info = "General articles on GenZ"
		elif st.session_state[WDGT_VS_CUR] == REDDIT_VS:
			src_info = "Reddit opinions"
		else:
			src_info = "No specific source information available"
	else:
		if src_type == SOURCE_MEDIUM:
			for item in doc_list:
				src = item.metadata.get("source")
				idx = item.metadata.get("start_index")
				src_info += "{" + src + " : " + str(idx) + "}\n"
		elif (src_type == SOURCE_SHORT) or (src_type == SOURCE_CLIP):   #CB240119
			src_info += "{"
			src_list = []
			for item in doc_list:
				src_long = item.metadata.get("source")
				src_short = source_pattern(src_long)
				if src_type == SOURCE_CLIP:     #CB240119
					src_short = src_short[0:7]    #CB240119
				if src_short not in src_list:
					src_list.append(src_short)
					src_info += " " + src_short + ","
			src_info = src_info[:-1] + " }"
	return src_info

#***********************
#
# Log File I/O
#
#***********************

def append_LogFile(text):
	timestamp = get_time_str()
	outfile = open(filename_logfile, "a")
	outstr = timestamp + " by " + " : " + text + "\n"
	outfile.write(outstr)
	outfile.close()
	return

def new_ChatFile():
	timestamp = get_time_str()
	# Create a Chat File
	st.session_state.filename_chatfile = (filename_save_root + "Chat_" +
	                                       "_" + timestamp + ".txt")
	print("New chat: ", st.session_state.filename_chatfile)
	outfile = open(st.session_state.filename_chatfile, "w")
	outfile.write("\n")
	outfile.close()
	# Create an Explain File
	st.session_state.filename_explainfile = (filename_save_root + "Explain_" 
	                                         + "_" + timestamp + ".txt")
	outfile = open(st.session_state.filename_explainfile, "w")
	outfile.write("\n")
	outfile.close()
	#enter that a new chat has started
	append_ChatFile_Activity("New Chat started with day/time --> " + timestamp, True)
	return

def append_ChatFile_Activity(text, explain_flag):
	append_ChatFile_label("Activity", text, True, explain_flag)
	return

def append_ChatFile_label(label, text, time_flag, explain_flag):
	timestamp = get_time_str()
	outfile = open(st.session_state.filename_chatfile, "a")
	if time_flag:
		outfile.write(TAB_0 + timestamp + " :\n")
	outfile.write(TAB_1 + label + " :\n")
	outfile.write(TAB_2 + text + "\n")
	outfile.close()
	if explain_flag:
		append_ExplainFile_label(timestamp, label, text, time_flag)
	return

def append_ExplainFile_label(timestamp, label, text, time_flag):
	#print("File: ", st.session_state.filename_explainfile)
	outfile = open(st.session_state.filename_explainfile, "a")
	if time_flag:
		outfile.write(TAB_0 + timestamp + " :\n")
	outfile.write(TAB_1 + label + " :\n")
	outfile.write(TAB_2 + text + "\n")
	outfile.close()
	return

def append_ChatResponse(question, response):
	append_ChatFile_label("** Question **", question, True, True)
	append_ChatFile_label("** Answer **", response, False, True)
	return

def append_ChatSources(sources):
	append_ChatFile_label("** Sources **", sources, False, False)
	return

def append_ExplainSources(sources):
	text = str(sources)
	append_ExplainFile_label("No time needed", "** Explain **", text, False)
	#print(sources)
	return

#***********************
#
# Vector Stores
#
#***********************

def set_VS_state(filename):
	st.session_state.filename_desiredVS = filename
	vectorstore = None
	#Assume Chroma-based unless Pivot, Articles,
	if (st.session_state[WDGT_VS_CUR] == PIVOT_VS) or \
		(st.session_state[WDGT_VS_CUR] == ARTICLE_VS) or \
			(st.session_state[WDGT_VS_CUR] == REDDIT_VS):
		vectorstore = get_vectorstore_fromdisk(st.session_state.filename_desiredVS)
	else:
		docsinfo = st.session_state.docscollection
		docinfo = docsinfo.get(filename)   #Which also includes the "Matrix" itself as a valid reference
		if docinfo is not None:
			coll_name = docinfo.get(KEY_COLLECTION)
			file_name = docinfo.get(KEY_FILENAME)
			vectorstore = get_vectorstore_fromdisk_Chroma(coll_name, file_name)
		else:
			print("***VS filename and collection not found")
	if vectorstore is not None:  # Check if vectorstore is assigned
		st.session_state.conversation = get_conversation_chain(vectorstore)
	else:
		print("***Vectorstore not initialized correctly")

	#st.session_state.conversation = get_conversation_chain(vectorstore)
	return

def set_vectorstore(filename, label):
	#CB240119 clear_chat_mem_hist()
	set_VS_state(filename)
	append_ChatFile_Activity("Now chatting with database: " + label, True)
	return

def get_vectorstore_fromdisk(filename):
	embeddings = OpenAIEmbeddings()
	vectorstore_cpu = FAISS.load_local(filename, embeddings, allow_dangerous_deserialization=True)
	return vectorstore_cpu

def get_vectorstore_fromdisk_Chroma(collname, filename):
	embeddings = OpenAIEmbeddings()
	vectorstore = Chroma(collection_name=collname, persist_directory=filename, embedding_function=embeddings)
	return vectorstore

def get_collection_names():
	docs_names = {}
	# set up the main Matrix VS name
	dict_item = {}
	dict_item[KEY_COLLECTION] = VS_ALL_PROJECT
	dict_item[KEY_FILENAME] = filename_vectorstore_Matrix
	docs_names[MATRIX_VS] = dict_item
	file_list = glob.glob(filebase_doc_vectorstore + '*')
	#print(file_list)
	for item in file_list:
		dict_item = {}
		dict_item[KEY_COLLECTION] = item.lower()
		dict_item[KEY_FILENAME] = filebase_doc_vectorstore + item
		docs_names[item] = dict_item
	#print(docs_names)
	return docs_names

#***********************
#
# Conversation Chain
#
#***********************

def get_conversation_chain(vectorstore):
	retriever = None
	temp = st.session_state[WDGT_CREATIVITY]/10.0
	llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=temp)
	st.session_state.memory = ConversationBufferMemory(memory_key=CHAT_HISTORY,input_key=CHAT_QUESTION, output_key=CHAT_ANSWER, return_messages=True)

	if vectorstore is not None and hasattr(vectorstore, 'as_retriever'):
		retriever = vectorstore.as_retriever(search_kwargs={"k": CHAT_NUM_DOCS_GET})
	else:
		print("***Invalid vectorstore or missing as_retriever method")
		return None
	
	conversation_chain = ConversationalRetrievalChain.from_llm(
		llm=llm,
		retriever=retriever,
		memory=st.session_state.memory,
		return_source_documents=True
	)
	
	print("Conversation reset")
	return conversation_chain

#***********************
#
# Document Column
#
#***********************

def get_matrix_docs():
	matrix_docs = {}
	df = pd.read_csv(filename_matrix_docs, header = 0)
	docs = df.to_dict("records")
	for item in docs:
		refid = item.get(KEY_REFID)
		key_yc = refid[:7]
		matrix_docs[key_yc] = item
	return matrix_docs

def handle_doc_request():
	key_num = st.session_state[WDGT_DOCNUM]
	#print("key entered: ", key_num)
	if key_num != None:
		docs = st.session_state.docsmatrix
		key_yc = key_num  #CB240119 = PROJECT_ID + str(key_num).zfill(5)
		doc = docs.get(key_yc)
		#need to check if exists
		with (st.session_state.doc_col):
			if doc == None:
				doc_display_textwarning("Document Doesn't exist")
			else:

				doc_display_textboxcool("Title:", doc.get(KEY_TITLE))
				doc_display_textareacool("Summary (created by the Chatbot):", doc.get(KEY_SUMMARY))
				doc_display_textboxcool("Reference:", doc.get(KEY_REFID))
				doc_display_textboxcool("Link to article/document:", doc.get(KEY_LINK))
				if st.session_state[WDGT_VS] != MATRIX_VS:
					doc_display_textmessage("Need YC-curated data to chat with this document only.")
				else:
					if st.toggle(label="Chat with this document only",key=WDGT_VSDOC)!=st.session_state[WDGT_VSDOC_CUR]:
						change_doc_vs(doc.get(KEY_REFID))
	return

def change_doc_vs(doc_id):
	# Requested a change of this document's vector state
	# Check if TRUE if desire use this documet's VS
	if st.session_state[WDGT_VSDOC]:
		# makesure MATRIX_VS has been the main selected...
		#		...it doesn't matter, but it makes the code simplier as:
		#				- can't make the main set of radio buttons none to show that not using them, even Matrix_VS
		#				- easy to reload when turning of this document as just reload Matrix_VS w/o knowing what was b4
		#				- LOL...can always claim need the Matrix VS to reader even if we actually don't :)
		if st.session_state[WDGT_VS] != MATRIX_VS:
			doc_display_textwarning("Need to have YC-curated database loaded first")
			#st.session_state[WDGT_VSDOC] = False
			st.session_state[WDGT_VSDOC_CUR] = False
		else:
			# load this document's vector store
			st.session_state[WDGT_VSDOC_CUR] = True
			set_vectorstore(doc_id, doc_id)
	else:
		# don't want this document's VS, so got back to Matrix VS
		st.session_state[WDGT_VSDOC_CUR] = False
		set_vectorstore(MATRIX_VS, MATRIX_VS)
	return

def doc_display_textboxcool(label, text):
	with stylable_container(
		key="container_woborder_txtbox",
		css_styles="""
			{
				color: black;
				font-weight: bold;
			}
			""",
	):
		st.write(label)
	with stylable_container(
		key="container_wborder_txtbox",
		css_styles="""
			{
				border-radius: 0.5em;
				padding: 5px;
				background-color: lightsteelblue;
			}
			""",
	):
		st.markdown(text)
	return

def doc_display_textareacool(label, text):
	with stylable_container(
		key="container_woborder_txtarea",
		css_styles="""
			{
				color: gray;
			}
			""",
	):
		st.write(label)
	st.text_area(label=label, value=text, disabled=True, height=200, label_visibility="collapsed")
	return

def doc_display_textwarning(label):
	with stylable_container(
		key="container_woborder_txtwarn",
		css_styles="""
			{
				color: red;
			}
			""",
	):
		st.write(label)
	return

def doc_display_textmessage(label):
	with stylable_container(
		key="container_woborder_txtwarn",
		css_styles="""
			{
				color: gray;
			}
			""",
	):
		st.write(label)
	return

def doc_display_textbox(label, text, disabled):
	st.text_input(label=label, value=text, disabled=disabled)
	return

def doc_display_textarea(label, text, disabled, height):
	st.text_area(label=label, value=text, disabled=disabled, height=height)
	return

#***********************
#
# Widget Control
#
#***********************

def set_Widgets_Init():
	st.session_state[WDGT_SOURCES] = WDGT_SOURCES_INIT
	st.session_state[WDGT_SOURCES_CUR] = WDGT_SOURCES_INIT
	st.session_state[WDGT_CREATIVITY] = WDGT_CREATIVITY_INIT
	st.session_state[WDGT_CREATIVITY_CUR] = WDGT_CREATIVITY_INIT
	st.session_state[WDGT_VS] = WDGT_VS_INIT
	st.session_state[WDGT_VS_CUR] = WDGT_VS_INIT
	st.session_state[WDGT_EMAIL_NAME] = None
	st.session_state[WDGT_DOCNUM] = None
	st.session_state[WDGT_VSDOC] = WDGT_VSDOC_INIT
	st.session_state[WDGT_VSDOC_CUR] = WDGT_VSDOC_INIT
	ssv[SS_CUR_CHAT_INPUT] = INIT_VAL_CHAT_INPUT
	print("Set wdgts to init")
	return

def set_Creativity():
	set_VS_state(st.session_state.filename_desiredVS)
	append_ChatFile_Activity("Chat creativity changed to --> " + str(st.session_state[WDGT_CREATIVITY]), True)
	return

def fresh_start():
	append_LogFile("Fresh Start")
	initial_state()
	print("Fresh Start")
	return

def do_reset(): 	#will eventually merge with fresh_start()
	set_Widgets_Init()
	print("Reset done")
	return

def onchange_question():
	user_question = ssv[SS_CHAT_WDGT_INPUT]
	#print("user_question: *" + str(user_question) + "*")
	if (user_question != INIT_VAL_CHAT_INPUT) and (user_question != "") and \
			(user_question != ssv[SS_CUR_CHAT_INPUT]):
		#print("processing question: *" + user_question + "*")
		handle_userinput(user_question)
		ssv[SS_CUR_CHAT_INPUT] = user_question
		#ssv[SS_CHAT_WDGT_INPUT_VALUE] = INIT_VAL_CHAT_INPUT
		#st.rerun()
		ssv[SS_CHAT_WDGT_INPUT] = INIT_VAL_CHAT_INPUT  #this is where it can be reset for display without error
	return

def disclaimer_seen():
	#print("***reviewed disclaimer")
	append_LogFile("Disclaimer reviewed")
	return

#***********************
#
# Email Control
#
#***********************


def send_chat_email(receiver_email):

	attach_filename = st.session_state.filename_chatfile
	shortname = attach_filename.split("/")[1]
	with open(attach_filename, "rb") as file:
		read_str = file.read()

	# create the email elements
	message = EmailMessage()
	message['From'] = sender_email
	message['To'] = receiver_email
	message['Subject'] = msg_subject

	#message.preamble = msg_body
	message.set_content(msg_body)
	message.add_attachment(read_str, maintype='text', subtype='utf-8', filename=shortname)

	# send it out via Gmail
	password = os.environ["MAIL_PSWD"]
	with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
		server.login(app_id, password)
		server.send_message(message)
	st.write("Email sent to: ", receiver_email)
	append_LogFile("Emailing " + st.session_state.filename_chatfile + " to: " + receiver_email)
	return


def send_chat_email2(receiver_email):
	# get the basic elements
	password = os.environ["MAIL_PSWD"]
	attach_filename = st.session_state.filename_chatfile
	# create the email elements
	message = MIMEMultipart()
	message['From'] = Header(sender_email)
	message['To'] = Header(receiver_email)
	message['Subject'] = Header(msg_subject)
	message.attach(MIMEText(msg_body, 'plain'))  #, 'utf-8'))
	# get the current chat as the file
	with open(attach_filename, "rb") as file:
		#attachment = MIMEApplication(file.read(), _subtype="txt")
		#part = MIMEBase("application", "octet-stream")
		part = MIMEBase("text", "plain")
		part.set_payload(file.read())
	#file.close()
	shortname = attach_filename.split("/")[1]
	part.add_header("Content-Disposition", "attachment", filename=shortname)
	                #f"attachment; filename={attach_filename}")
	message.attach(part)
	# send it out via Gmail
	with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
		server.login(app_id, password)
		server.sendmail(sender_email, receiver_email, message.as_string())
		#server.quit()
	st.write("Chat emailed to: ", receiver_email)
	append_LogFile("Emailing " + st.session_state.filename_chatfile + " to: " + receiver_email)
	return


#***********************
#
# Set up System
#
#***********************

def initial_state():
	set_Widgets_Init()
	clear_chat_mem_hist()
	set_VS_state(filename_vectorstore_Pivot)
	new_ChatFile()
	append_ChatFile_Activity("Now chatting with database: " + st.session_state[WDGT_VS_CUR], True)
	append_LogFile("Init Chat: " + st.session_state.filename_chatfile)
	return

def get_time_str():
	#time_start = time.asctime()
	#time_start = time_start.replace(" ", "_")
	#time_start = time_start.replace(":", "-")
	time_gmt = time.gmtime()
	time_start = time.strftime("%Y-%m-%d_%H:%M:%S-GMT", time_gmt)

	return time_start


def main():

	st.set_page_config(page_title=title_string, layout="wide", menu_items=None)
	st.markdown(pagecss, unsafe_allow_html=True)
	#st.header(title_string)
	#st.header("")

	st.session_state.mysidebar,st.session_state.chat_col,st.session_state.doc_col = \
		st.columns([0.2,0.6,0.3],gap="medium")


	# if "security_setup" not in st.session_state:
	# 	security_setup()
	# 	st.session_state["security_setup"] = True

	#st.session_state.login_auth.login()

	#login()

	if 'logged_in' not is st.session_state:
		st.session_state['logged_in'] = False

	if st.session_state['logged_in']:
		

	# if login():
	# 	st.session_state["authentication_status"] = True
	# if st.session_state["Not_1st_time"] is False:
	# 	with (st.session_state.chat_col):
	# 		st.image("images/YC_summit_logo_sm.png", width=250)
	# 		security_login()


	#if security_allowed_entry():
		#st.session_state 
		if CHAT_STATE_INIT_DONE not in st.session_state:
			with st.spinner("Loading documents..."):
				st.session_state.docsmatrix = get_matrix_docs()
				if not st.session_state.docsmatrix:
					st.error("Failed to load documents.")
					return  # Optionally halt further execution
				st.session_state.docscollection = get_collection_names()
				initial_state()
				st.session_state[CHAT_STATE_INIT_DONE] = True
		#user_question = st.chat_input(prompt_string)
	
		with (st.session_state.mysidebar):
	
			st.markdown(script_col_noscroll, unsafe_allow_html=True)
	
			st.image("images/YC_summit_logo_sm.png", width=150)
	
			#CB240119 userid = st.session_state["username"]
			#userstr = userid.split("@")[0]
			#doc_display_textmessage("Hello, *" + userstr + "*")
			#CB240119 st.write("Hello, *" + userid + "*")
	
			if st.radio("Select Database:", [PIVOT_VS, ARTICLE_VS, REDDIT_VS, MATRIX_VS],
						#captions=[PIVOT_DESC, ARTICLE_DESC, REDDIT_DESC, MATRIX_DESC],  #CB240119
						key=WDGT_VS) != \
				st.session_state[WDGT_VS_CUR]:
					st.session_state[WDGT_VS_CUR] = st.session_state[WDGT_VS]
					if st.session_state[WDGT_VS_CUR] == PIVOT_VS:
						st.session_state.filename_desiredVS = filename_vectorstore_Pivot
					if st.session_state[WDGT_VS_CUR] == ARTICLE_VS:
						st.session_state.filename_desiredVS = filename_vectorstore_Article
					if st.session_state[WDGT_VS_CUR] == REDDIT_VS:
						st.session_state.filename_desiredVS = filename_vectorstore_Reddit
					if st.session_state[WDGT_VS_CUR] == MATRIX_VS:
						st.session_state.filename_desiredVS = MATRIX_VS
					set_vectorstore(st.session_state.filename_desiredVS, st.session_state[WDGT_VS_CUR])
	
	
			#if st.slider("Creativity Level", 0, 10, key=WDGT_CREATIVITY) != st.session_state[WDGT_CREATIVITY_CUR]:
			#	set_Creativity()
			#	st.session_state[WDGT_CREATIVITY_CUR] = st.session_state[WDGT_CREATIVITY]
			#	print("Temp slider changed")
	
			#if st.toggle("Show Sources", key=WDGT_SOURCES) != st.session_state[WDGT_SOURCES_CUR]:
			#	st.session_state[WDGT_SOURCES_CUR] = st.session_state[WDGT_SOURCES]
			#	print("Sources toggle changed")
	
			st.divider()
	
			#st.text_input("Email address:", placeholder="enter your email address",
			#			  key=WDGT_EMAIL_NAME, value=None, label_visibility="collapsed")
	
	
			#st.divider()
	
			if st.button("Clear Chat Q&A"):
				clear_chat_mem_hist()
				set_VS_state(st.session_state.filename_desiredVS)
				#st.write(st.session_state[WDGT_VS_CUR], " chat has been cleared.")
				append_ChatFile_Activity("Cleared Chat for database --> " + st.session_state[WDGT_VS_CUR],True)
	
			if st.button("Email Chat Session"):
				#if st.session_state[WDGT_EMAIL_NAME] == None:
				#	doc_display_textwarning("Need an email name")
				#else:
				#	send_chat_email(st.session_state[WDGT_EMAIL_NAME])
				send_chat_email(st.session_state["username"])
	
			#st.button("Fresh Start", on_click=fresh_start)
	
			# st.button("Reset", on_click=do_reset)
	
			#st.session_state.login_auth.logout("Logout", 'main')
			if st.button("Logout"):
				append_LogFile("Logout")
				append_ChatFile_Activity("Logout", False)
				print(" logged out")
				st.session_state["authentication_status"] = False
				st.session_state["Not_1st_time"] = False
				del st.session_state[CHAT_STATE_INIT_DONE]
				st.rerun()
	
			st.divider()
	
			if st.button("Disclaimer"):
				with st.form("Disclaimer"):
					st.write(disclaimer)
					st.form_submit_button("Okay", on_click=disclaimer_seen)
	
		with st.session_state.chat_col:
	
			if len(st.session_state.display_chat) != 0:  # if there is something in the chat to display, make the column reverse
				st.markdown(script_col_scroll, unsafe_allow_html=True)
			else:
				st.markdown(script_col_noscroll, unsafe_allow_html=True)
	
			#st.image("images/YC_summit_logo_sm.png", width=250)   #CB240119
			st.markdown(csschat, unsafe_allow_html=True)
	
			st.header(title_string)
	
			#CB240119
			#userid = user
			hello_usr = r'''$\textsf{\normalsize Hello,}$'''
			st.markdown(hello_usr + " *" + "userid" + "*")
	
			#CB240119:
			info_title = r'''$\textsf{\normalsize You can chat with 4 types of information:}$'''
			st.write(info_title)
			info_db = ":large_orange_circle: **" + PIVOT_VS + "** - *" + PIVOT_DESC + "*" + "  \n"
			info_db = info_db + ":large_yellow_circle: **" + ARTICLE_VS + "** - *" + ARTICLE_DESC + "*"  + "  \n"
			info_db = info_db + ":large_green_circle: **" + REDDIT_VS + "** - *" + REDDIT_DESC + "*"  + "  \n"
			info_db = info_db + ":large_purple_circle: **" + MATRIX_VS + "** - *" + MATRIX_DESC + "*"
			st.markdown(info_db)
	
	
	
	
	
			#Changes to get a better user input line for chat
			display_Chat()
			user_question = st.text_input(CHAT_PROMPT_STRING,
										  value=INIT_VAL_CHAT_INPUT,
										  on_change=onchange_question,
										  key=SS_CHAT_WDGT_INPUT)
			#if user_question:
			#	handle_userinput(user_question)
	
			#display_Chat()
	
	
		with st.session_state.doc_col:
	
			st.markdown(script_col_noscroll, unsafe_allow_html=True)
	
			st.header("Explore Documents")
	
			if st.session_state[WDGT_VS_CUR] == MATRIX_VS:
				#CB240119 st.number_input("Enter Doc# (from yc#####-cccc-aaaa)", min_value=0, value=None,
				#CB240119												format="%d", step=None, key=WDGT_DOCNUM)
				st.text_input("Enter Document - YC#####", value=None, max_chars=7, key=WDGT_DOCNUM)
				handle_doc_request()
			else:
				doc_display_textmessage("Need YC-curated database set in order to use.")
	
		st.markdown(script_col_active, unsafe_allow_html=True)

	else:
		login()




if __name__ == '__main__':
	main()
