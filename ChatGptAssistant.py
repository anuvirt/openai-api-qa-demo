from openai import OpenAI
import os, sys


class ChatGptAssistant():

    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    def __init__(self, verbose=False):
        #Only one assistant, one thread and one run at the time!!!!
        self.verbose = verbose
        self.assistant = None
        self.thread = None
        self.run = None
        #{name:{id, fileObj}
        self.files = {}
        self.client = None

        self.apikey = os.environ.get('OPENAI_API_KEY')
        if self.apikey in ["", None]:
            raise ValueError("OPENAI_API_KEY value not given")



    #######################
    ## Keyword Funcitons ##
    #######################

    def prepare_assistant(self, name, description= None):
        self.client = self._client_create()

        self.assistant = self._assistant_create(name, description)
        self.thread = self._thread_create()

    def add_file_to_assistant(self, name, filepath):
        # Create a vector store
        vector_store = self.client.beta.vector_stores.create(name=name)

        # Ready the files for upload to OpenAI
        file_paths = [filepath]
        file_streams = [open(path, "rb") for path in file_paths]

        # Use the upload and poll SDK helper to upload the files, add them to the vector store,
        # and poll the status of the file batch for completion.
        file_batch = self.client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=file_streams
        )

        # You can print the status and the file counts of the batch to see the result of this operation.
        print(file_batch.status)
        print(file_batch.file_counts)
        assistant = self.client.beta.assistants.update(
            assistant_id=self.assistant.id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
        )


    def ask_question_from_assistant(self, message):
        messageObj = self._thread_add_message(self.thread.id, message)
        run = self._run_create(self.thread.id, self.assistant.id)
        self._run_wait_processed(run, self.thread.id)
        answer = self._run_get_answer(self.thread.id, messageObj)
        return answer

    def clear_assistant_converstion_history(self):
        self._thread_delete(self.thread)
        self.thread = None

    def delete_files(self):
        for file in self.files:
            self._file_delete(self.files[file]["id"])
        self.files = {}

    def delete_assistant(self):
        if self.thread != None:
            self.clear_assistant_converstion_history
        self.delete_files()
        self._assistant_delete(self.assistant.id)
        self.assistant = None




    ########################
    ## Internal Funcitons ##
    ########################

    ### Client functions
    def _client_create(self):
        # Initialize OpenAI API client with your API key
        client = OpenAI(api_key=self.apikey, default_headers={"OpenAI-Beta": "assistants=v2"})
        if self.verbose:
            print("Client props:")
            print(client)
        return client

    ### Assistant functions
    def _assistant_create(self, name, description=None):
        if self.verbose:
            print("- - Creating Assistant:")
        if description:
            desc=description
        else:
            desc = "You are a test automation specialist specialiced on web page testing. You do \
                    testing using using robot framework with a \
                    selenium library. You will give working examples of robot code as part of the answer \
                    when asked a question"
        assistant = self.client.beta.assistants.create(
            name=name,
            instructions=desc,
            model="gpt-4o",
            tools=[{"type": "code_interpreter"},
    {
      "type": "file_search"
    }]
        )
        if self.verbose:
            print("Assistant props:")
            print(assistant)
        return assistant

    def _assistant_list(self):
        if self.verbose:
            print("- - Listing Assistant:")
        assistants = self.client.beta.assistants.list()
        if self.verbose:
            print("Assistants list:")
            for assistant in assistants:
                print("Name: %s\t\tId: %s" % (assistant.name, assistant.id))
        return assistants

    def _assistant_delete(self, assistantid):
        if self.verbose:
            print("- - Deleting Assistant:")
        result = self.client.beta.assistants.delete(
            assistant_id=assistantid
        )
        if self.verbose:
            print("Assisntant deleted:")
            print(result)
        return result

    def _assistant_add_file(self, assistantid, fileid):
        if self.verbose:
            print("- - Attaching File To Assistant:")
        result = self.client.beta.assistants.files.create(
            assistant_id=assistantid,
            file_id=fileid
        )
        if self.verbose:
            print("Assisntant File props:")
            print(result)



        return result

    def _assistant_delete_file(self, assistantid, fileid):
        if self.verbose:
            print("- - Detaching File From Assistant:")
        result = self.client.beta.assistants.files.delete(
            assistant_id=assistantid,
            file_id=fileid
        )
        if self.verbose:
            print("Assisntant File Detach:")
            print(result)
        return result

    def _assistant_get_instance(self, assistantid):
        if self.verbose:
            print("- - Getting Assistant:")
        assistant = self.client.beta.assistants.retrieve(
            assistant_id=assistantid
        )
        if self.verbose:
            print("Assisntant props:")
            print(assistant)
        return assistant


    ### File operations
    def _files_list(self):
        if self.verbose:
            print("- - Listing Files:")
        files = self.client.files.list()
        if self.verbose:
            print("Files list:")
            for file in files:
                print("Name: %s\t\tId: %s" % (file.filename, file.id))
        return files

    def _file_upload(self, content):
        if self.verbose:
            print("- - Uploading File:")
        # Upload a file with an "assistants" purpose
        fileobj = self.client.files.create(
            file=open(content, "rb"),
            purpose='assistants'
        )
        if self.verbose:
            print("File props:")
            print(fileobj)
        return fileobj

    def _file_delete(self, fileid):
        if self.verbose:
            print("- - Deleting File: %s" % fileid)
        # Delete file from openai storage
        deletion = self.client.files.delete(
            file_id=fileid
        )
        if self.verbose:
            print("File deletion:")
            print(deletion)
        return deletion


    #Thread operations
    def _thread_create(self):
        if self.verbose:
            print("- - Creating Thread:")
        # Create a thread where the conversation will happen
        thread = self.client.beta.threads.create()
        if self.verbose:
            print("Thread:")
            print(thread)
        return thread

    def _thread_delete(self, threadid):
        if self.verbose:
            print("- - Delete Thread:")
        # Delete thread from assistant
        result = self.client.beta.threads.delete(
            thread_id=threadid
        )
        if self.verbose:
            print("Assisntant props:")
            print(result)
        return result

    def _thread_add_message(self, threadid, message):
        if self.verbose:
            print("- - Adding Message To Thread:")
        # Create the user message and add it to the thread
        message = self.client.beta.threads.messages.create(
            thread_id=threadid,
            role="user",
            content=message
        )
        if self.verbose:
            print("Message:")
            print(message)
        return message

    #Run operations
    def _run_create(self, threadid, assistantid):
        if self.verbose:
            print("- - Creating Run:")
        # Create the Run, passing in the thread and the assistant
        run = self.client.beta.threads.runs.create(
            thread_id=threadid,
            assistant_id=assistantid
        )
        if self.verbose:
            print("Run:")
            print(run)
        return run

    def _run_wait_processed(self, run, threadid):
        if self.verbose:
            print("- - Waiting For Processing To be Done:")
        # Periodically retrieve the Run to check status and see if it has completed
        # Should print "in_progress" several times before completing
        while run.status != "completed":
            keep_retrieving_run = self.client.beta.threads.runs.retrieve(
                thread_id=threadid,
                run_id=run.id
            )
            print(f"Run status: {keep_retrieving_run.status}")

            if keep_retrieving_run.status == "completed":
                print("\n")
                break

    def _run_get_answer(self, threadid, message):
        if self.verbose:
            print("- - Getting Answers:")
        # Retrieve messages added by the Assistant to the thread
        all_messages = self.client.beta.threads.messages.list(
            thread_id=threadid
        )
        # Print the messages from the user and the assistant
        answer = ""
        answer += "\n######################################################"
        answer += "\nUSER: %s" % message.content[0].text.value
        answer += "\nASSISTANT: %s" % all_messages.data[0].content[0].text.value
        answer += "\n######################################################"

        if self.verbose:
            print(answer)
        return answer


    def store_to_file(self, name, data):
        f = open(name, "w")
        f.write(data)
        f.close()




if __name__ == "__main__":

    # # TEST BASIC COMMUNICATION
    # print("Hello World")
    # oracle = ChatGptAssistant(verbose=True)
    # oracle.prepare_assistant("testAssisant")
    # oracle.ask_question_from_assistant("On what coutry is Rovaniemi?")
    # oracle.ask_question_from_assistant("What is the capital of that country?")
    # oracle.ask_question_from_assistant("What is the population of that capital?")
    # oracle.delete_assistant()

    # TEST BASIC FILE USAGE
    print("Hello World")
    oracle = ChatGptAssistant(verbose=True)
    oracle.prepare_assistant("testAssisant")
    oracle.add_file_to_assistant("testfilez", "page.html")
    oracle.ask_question_from_assistant("how to do a working login test on provided html format page.html file. Use locators and data from the provided html file")
    oracle.delete_assistant()
