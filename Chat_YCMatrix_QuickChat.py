
import streamlit as st
from streamlit import session_state as ssv
import streamlit_authenticator as stauth

from dotenv import load_dotenv
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai.chat_models import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from htmlTemplateAltInno_page import pagecss
from htmlTemplateAltInno_chat import csschat, bot_template, user_template

from quickchat_literals import *

import time
import glob
import yaml


#***********************
#
# Load OpenAI access keys
#
#***********************

load_dotenv()


#***********************
#
# Security ... this set of routines may get dropped once a higher level of security is added prior to this chat system
#
#***********************

def security_reset_user_file( userid, password, flag_1st):
	filename_yaml_user = SECURE_FILEDIR_USERS + userid + ".yaml"
	with open(filename_yaml_user, 'r') as file:
		user_data = yaml.safe_load(file)
		user_data[SECURE_KEY_USERINFO][userid][SECURE_KEY_PASSWORD] = password
		user_data[SECURE_KEY_FLAG_FIRSTTIME] = flag_1st
	with open(filename_yaml_user, "w") as file:
		yaml.dump(user_data, file, default_flow_style=False)
	return

def security_allowed_entry():
	entry_ok = False
	if ssv[SS_AUTH_STATUS] and ssv[SECURE_FLAG_USERIN]:
		entry_ok = True
	return entry_ok

def security_setup():
	#***build up the user dictionary for the login credentials + the flags indicating if each user has signed in before
	users_list = {}
	ssv[SS_SECURE_DICT_FLAG_FIRSTTIME] = {}
	for user_file in glob.glob(SECURE_FILEDIR_USERS + "*.*"):
		with open(user_file, 'r') as file:
			#build up the credential list of users
			user_data = yaml.safe_load(file)
			userinfo = user_data[SECURE_KEY_USERINFO]
			users_list.update(userinfo)
			#build up the dictionary of 1st time flags
			keyslist = list(userinfo)
			username = keyslist[0]
			ssv[SS_SECURE_DICT_FLAG_FIRSTTIME][username] = user_data[SECURE_KEY_FLAG_FIRSTTIME]

	#create the base credential dictionary for the login routine
	ssv[SS_DICT_CREDENTIALS] = {}
	ssv[SS_DICT_CREDENTIALS][SECURE_KEY_USERNAME_LIST] = users_list

	#load the default cookie, even though cookies not used
	with open(SECURE_FILENAME_COOKIE, 'r') as file:
		cookie_data = yaml.safe_load(file)

	#create the authentication profile for the security signin
	ssv[SS_LOGIN_AUTH] = stauth.Authenticate(
		ssv[SS_DICT_CREDENTIALS],
		cookie_data[SECURE_KEY_COOKIE][SECURE_KEY_NAME],
		cookie_data[SECURE_KEY_COOKIE][SECURE_KEY_KEY],
		cookie_data[SECURE_KEY_COOKIE][SECURE_KEY_EXPIRE]
	)

	#set up the flag to check if a user has been signed in for the initialization process
	ssv[SECURE_FLAG_USERIN] = False

	return

def security_login():

	st.session_state.login_auth.login()
	if ssv[SS_AUTH_STATUS]:   #check user has been authorized via login dialogue box
		if ssv[SS_SECURE_DICT_FLAG_FIRSTTIME][ssv[SECURE_KEY_USERNAME]]:   #if user not signed in before, change password
			#print("Need to request change of password")
			#append_LogFile("1st-time signin --> still needs password changed")
			try:
				if st.session_state.login_auth.reset_password(ssv[SECURE_KEY_USERNAME],
										fields={'Form name': 'First Time User - Reset Password:'}):
					st.success('Password modified successfully')
					userid = ssv[SECURE_KEY_USERNAME]
					ssv[SS_SECURE_DICT_FLAG_FIRSTTIME][userid] = False
					security_reset_user_file( userid,
					                 ssv[SS_DICT_CREDENTIALS][SECURE_KEY_USERNAME_LIST][userid][SECURE_KEY_PASSWORD],
					                 ssv[SS_SECURE_DICT_FLAG_FIRSTTIME][userid])
					ssv[SECURE_FLAG_USERIN] = True
					time.sleep(3)
					st.rerun()
			except Exception as e:
				st.error(e)
		else:
			ssv[SECURE_FLAG_USERIN] = True  # signin is successful
	elif ssv[SS_AUTH_STATUS] is False:   #login failed?
		st.error("Username and/or password is incorrect")
	elif ssv[SS_AUTH_STATUS] is None:  #login empty?
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
		response = ssv[CHAT_STATE_CONVERSATION].invoke({CHAT_QUESTION: user_question})
	except Exception as e:
		error_msg = "Sorry, there seems to be an issue with your question. It is likely" + \
			" that the server is down to find your answer. Please try again with a slightly different " + \
			" question, or you might even have to try later when the server comes up again."
		response = { CHAT_QUESTION : user_question, CHAT_ANSWER : error_msg}
		source_info = " { System Down } "	# save all the elements of the response
	append_ChatDisplay(response[CHAT_QUESTION], response[CHAT_ANSWER])
	return

def onchange_question():
	user_question = ssv[SS_CHAT_WDGT_INPUT]
	if (user_question != INIT_VAL_CHAT_INPUT) and (user_question != "") and \
			(user_question != ssv[SS_CUR_CHAT_INPUT]):
		handle_userinput(user_question)
		ssv[SS_CUR_CHAT_INPUT] = user_question
		ssv[SS_CHAT_WDGT_INPUT] = INIT_VAL_CHAT_INPUT  #this is where it can be reset for display without error
	return

def display_Chat():
	for dispmessage in ssv[SS_DISPLAY_CHAT]:
		with st.chat_message(CHAT_USER, avatar=CSS_USER_AVATAR):
			st.write(user_template.replace(CSS_MESSAGE_REPLACE, dispmessage[CHAT_QUESTION]), unsafe_allow_html=True)
		with st.chat_message(CHAT_ASSISTANT, avatar=CSS_ROBOT_AVATAR):
			st.write(bot_template.replace(CSS_MESSAGE_REPLACE, dispmessage[CHAT_ANSWER]), unsafe_allow_html=True)
	return

def clear_chat_mem_hist():
	ssv[CHAT_STATE_MEMORY] = None
	ssv[SS_DISPLAY_CHAT] = []
	return

def append_ChatDisplay(question, answer):
	ssv[SS_DISPLAY_CHAT].append({ CHAT_QUESTION : question, CHAT_ANSWER : answer })
	return


#***********************
#
# Vectorstores of documents & Conversation chain for chatting
#
#***********************

def set_vectorstore(coll_name, filename):
	# normally would have done coll_name.lower(), but the original was done with upper YC
	vectorstore = get_vectorstore_fromdisk_Chroma(coll_name, filename)
	ssv[CHAT_STATE_CONVERSATION] = get_conversation_chain(vectorstore)
	return

def get_vectorstore_fromdisk_Chroma(collname, filename):
	embeddings = OpenAIEmbeddings()
	vectorstore = Chroma(collection_name=collname, persist_directory=filename, embedding_function=embeddings)
	return vectorstore

def get_conversation_chain(vectorstore):
	temp = CHAT_CREATIVITY_INIT/10.0
	llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=temp)
	ssv[CHAT_STATE_MEMORY] = ConversationBufferMemory(memory_key=CHAT_HISTORY,
													   input_key=CHAT_QUESTION, output_key=CHAT_ANSWER,
													   return_messages=True)
	conversation_chain = ConversationalRetrievalChain.from_llm(
		llm=llm,
		retriever=vectorstore.as_retriever(search_kwargs={"k":CHAT_NUM_DOCS_GET}),
		memory=ssv[CHAT_STATE_MEMORY],
		return_source_documents=True
	)
	return conversation_chain

#***********************
#
# Widget Control
#
#***********************

def set_widgets_init():
	ssv[SS_CUR_CHAT_INPUT] = INIT_VAL_CHAT_INPUT
	return


#***********************
#
# Set up System upon first time a user has signed in
#
#***********************

def initial_state():
	set_widgets_init()
	clear_chat_mem_hist()
	set_vectorstore(VS_MATRIX_NAME, VS_MATRIX_FILE)
	return


def main():

	# set up the streamlit configuration
	st.set_page_config(page_title=CHAT_TITLE, menu_items=None)
	st.markdown(pagecss, unsafe_allow_html=True)

	# check if security system has been set up before
	if SECURE_FLAG_SETUP not in st.session_state:
		security_setup()
		ssv[SECURE_FLAG_SETUP] = True

	# check to see if user has signed in yet
	if 	ssv[SECURE_FLAG_USERIN] is False:
		st.image(FILE_LOGO, width=250)
		security_login()

	# if the user has been allowed in, they can continue to chat
	if security_allowed_entry():

		if CHAT_STATE_INIT_DONE not in st.session_state:   #make sure the system gets set up first time user signed in
			initial_state()
			ssv[CHAT_STATE_INIT_DONE] = True

		with st.container(height=500, border=True):
			st.image(FILE_LOGO, width=150)

			st.header(CHAT_TITLE)

			display_Chat()

			user_question = st.text_input(CHAT_PROMPT_STRING,
										  value=INIT_VAL_CHAT_INPUT,
										  on_change=onchange_question,
										  key=SS_CHAT_WDGT_INPUT)

			#using the provided streamlit chat prompt ... which has issues
			#user_question = st.chat_input(CHAT_PROMPT_STRING)
			#if user_question:
			#	handle_userinput(user_question)

		if st.button("Logout"):
			ssv[SS_AUTH_STATUS] = False
			ssv[SECURE_FLAG_USERIN] = False
			del st.session_state[CHAT_STATE_INIT_DONE]
			st.rerun()


# End of MAIN


if __name__ == '__main__':
	main()
