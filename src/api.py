import json
import os

import cherrypy
import hydra
import rootutils
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from loguru import logger
from omegaconf import DictConfig

rootutils.setup_root(__file__, indicator="pyproject.toml", pythonpath=True)


class VectorDBAPI:

    def __init__(self, cfg: DictConfig):
        logger.info("Initializing VectorDB API. Please wait...")

        # hydra config
        self.cfg: DictConfig = cfg

        # Data classes
        self.dataloader = TextLoader
        self.text_splitter = hydra.utils.instantiate(cfg.text_splitter)

        # embedding classes
        self.embedding = hydra.utils.instantiate(cfg.model)

        # Vector database
        self.vector_db = None

        # Create directories for saving data
        for path_key in ["data_save", "data_loaded", "data_queried"]:
            os.makedirs(self.cfg.paths.get(path_key), exist_ok=True)

        # Initialize the vector database with the data in the data directory
        self.add_document_to_database(file_path=self.cfg.paths.get("data_dir"))

        logger.info("Endpoint ready.")

    @cherrypy.expose
    def index(self):
        return """
            <html>
            <body>
                <h2>Upload a text file</h2>
                <form action="upload" method="post" enctype="multipart/form-data">
                    <input type="file" name="file" />
                    <input type="submit" value="Upload" />
                </form>
                <h2>Retrieve Similar Documents</h2>
                <form action="retrieve_similar" method="post" enctype="multipart/form-data">
                    <input type="file" name="file" />
                    <input type="submit" value="Retrieve" />
                </form>
            </body>
            </html>
        """

    @cherrypy.expose
    def upload(self, file):
        """
        Endpoint to handle file upload.
        The file will be saved and its content added to the vector database defined in the hydra config.
        """
        if not file.filename.endswith(".txt"):
            raise cherrypy.HTTPError(400, "Only text files are supported.")

        upload_path = os.path.join(self.cfg.paths.get("data_save"), file.filename)

        # make sure the path exists, if not create it
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)

        # Save uploaded file to disk
        with open(upload_path, "wb") as out:
            while True:
                data = file.file.read(8192)
                if not data:
                    break
                out.write(data)

        # Process and add the uploaded file to the vector store
        self.add_document_to_database(self.cfg.paths.get("data_save"))

        return f"File '{file.filename}' uploaded and added to vector database."

    @cherrypy.expose
    def retrieve_similar(self, file):
        """
        Endpoint to retrieve similar documents from the vector database given a query document.
        """
        upload_path = os.path.join(self.cfg.paths.get("data_save"), file.filename)

        # Save uploaded query file to disk
        with open(upload_path, "wb") as out:
            while True:
                data = file.file.read(8192)
                if not data:
                    break
                out.write(data)

        # Retrieve similar documents based on the uploaded query file
        similar_documents = self.get_similar_documents(self.cfg.paths.get("data_save"))

        if similar_documents:
            return similar_documents
        else:
            return "No similar documents found."

    def add_document_to_database(self, file_path):
        """
        Add a document(s) to the vector database.
        """
        loaded_document = DirectoryLoader(
            path=file_path,
            glob="**/*.txt",
            loader_cls=self.dataloader,
        ).load()

        # move all the files in the data_save directory to the data_loaded directory
        if file_path == self.cfg.paths.get("data_save"):
            for file in os.listdir(self.cfg.paths.get("data_save")):
                os.rename(
                    os.path.join(self.cfg.paths.get("data_save"), file),
                    os.path.join(self.cfg.paths.get("data_loaded"), file),
                )

        # Let's get chunky (｡･･｡)
        chunked_documents = self.text_splitter.split_documents(loaded_document)

        # Load the existing vector database or create a new one if it doesn't exist
        if self.vector_db is None:
            self.vector_db = hydra.utils.call(
                self.cfg.get("db"), chunked_documents, embedding=self.embedding
            )
        else:
            self.vector_db.add_documents(chunked_documents, embedding=self.embedding)

    def get_similar_documents(self, query_file_path):
        """
        Retrieve similar documents from the vector database given a query document.
        """
        # Load the query document
        query_document = DirectoryLoader(
            path=query_file_path,
            glob="**/*.txt",
            loader_cls=self.dataloader,
        ).load()

        # move all the files in the data_save directory to the data_queried directory
        if query_file_path == self.cfg.paths.get("data_save"):
            for file in os.listdir(self.cfg.paths.get("data_save")):
                os.rename(
                    os.path.join(self.cfg.paths.get("data_save"), file),
                    os.path.join(self.cfg.paths.get("data_queried"), file),
                )

        # Perform similarity search in the vector database
        search_results = self.vector_db.similarity_search(
            query_document[0].page_content, k=self.cfg.get("num_results")
        )

        # Extract and return the metadata of the similar documents (e.g., file paths)
        similar_documents = [result.metadata.get("source") for result in search_results]

        return json.dumps({"similar_documents": similar_documents})


@hydra.main(version_base="1.3", config_path="../configs", config_name="deploy")
def main(cfg: DictConfig):
    cherrypy.quickstart(
        VectorDBAPI(cfg),
        "/",
        {
            "/": {
                "tools.staticdir.root": os.path.abspath(os.getcwd()),
                "tools.staticdir.on": True,
                "tools.staticdir.dir": "html",
                "tools.staticdir.index": "index.html",
            }
        },
    )


if __name__ == "__main__":
    main()
