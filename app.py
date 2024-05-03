# from openai import OpenAI
import openai
import streamlit as st

st.title("SEERAH BOT")

client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
from typing_extensions import override
from openai import AssistantEventHandler
def insertTodb(query,response):
    import pymongo
    client = pymongo.MongoClient(st.secrets["MONGO_URI"])
    db = client.books
    db.seerahbooks.insert_one({"user":st.session_state.name, "query":query,"response":response})
    
class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        print(f"", end="", flush=True)

    @override
    def on_tool_call_created(self, tool_call):
        print(f"{tool_call.type}\n", flush=True)

    @override
    def on_message_done(self, message) -> None:        
        # Extract the message content
        message_content = message.content[0].text
        annotations = message_content.annotations
        citations = []
        
        # Iterate over the annotations and add footnotes
        for index, annotation in enumerate(annotations):
            # Replace the text with a footnote
            message_content.value = message_content.value.replace(annotation.text, f' [{index}]')
        
            # Gather citations based on annotation attributes
            if (file_citation := getattr(annotation, 'file_citation', None)):
                cited_file = client.files.retrieve(file_citation.file_id)
                qt=file_citation.quote
                if qt:
                    citations.append(f'[{index}] {qt} from {cited_file.filename}')
                else:
                    citations.append(f'[{index}] from {cited_file.filename}')
                
            elif (file_path := getattr(annotation, 'file_path', None)):
                cited_file = client.files.retrieve(file_path.file_id)
                citations.append(f'[{index}] Click <here> to download {cited_file.filename}')
                # Note: File download functionality not implemented above for brevity
        
        # Add footnotes to the end of the message before displaying to user
        message_content.value += '\n' + '\n'.join(citations)
        
        st.session_state.messages.append({"role": "assistant", "content": message_content.value})
        
        response = st.write(message_content.value)# +"\nCitations: ".join(citations)  )
        insertTodb(st.session_state.messages[-2]["content"],message_content.value)
        # print(response)
        # print("Citations\n".join(citations))

       

if "name"  in st.session_state and "checked" in st.session_state :
    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": st.session_state.name+" asks "+prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            
            thread = client.beta.threads.create(
            messages=[
                    {"role": "user", "content": prompt}
                    # for m in st.session_state.messages
                ],
                    # ,
                # tool_resources={
                #     "file_search": {
                #     "vector_store_ids": ["vs_gPspfa4idD83ozY9M28BsHox"]
                #     }
                # }
                # event_handler=EventHandler()
            )
            # report=[]
            # for event in streams:
            #     if event.data.object=="thread.message.delta":
            #         for content in event.data.delta.content:
            #             if content.type=="text":
            #                 report.append(content.value)
            #                 st.session_state.messages.append({"role": "assistant", "content": content.value})
                            # resul=
            with client.beta.threads.runs.stream(
                thread_id=thread.id,
                assistant_id=st.secrets["assistant_id"] ,
                instructions="Please address the user as Seerah Bot. The user has a premium account.",
                event_handler=EventHandler(),
            ) as stream:
                    stream.until_done()
            # response = st.write_stream(streams)
        
            # st.session_state.messages.append({"role": "assistant", "content": response})
else:
    with st.form("my_form"):
        user = st.text_input("Your Good name", "")
        if "name"  in st.session_state:
        
            st.write("Assalamoalikum ", st.session_state.name, " Welcome to Seerah Bot, How can I help you today?")
        else:
            st.write("Assalamoalikum ", user, " Welcome to Seerah Bot, How can I help you today?")

        checkbox_val = st.checkbox("I here by share my query to Seerah Bot, and it can be used for training purposes.")

        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.session_state.name=user
            if checkbox_val:
                st.session_state.checked=True
                st.write("May Allah give barakah in your knowledge and help you in your journey to learn more about Seerah.")
   
