from chromadb.api.models import Collection as ChromaDBCollection
from django.conf import settings
from chromadb.utils import embedding_functions
import chromadb


class ChromaDBSingleton:
    """
    A singleton class to provide a single point of access for ChromaDB.

    This singleton initializes the default embedding function, creates a ChromaDB client,
    and sets up a default collection.

    Attributes:
        default_ef: The default embedding function.
        client: The ChromaDB persistent client.
        collection: The default collection for the client.

        Usage:
        chroma_db = ChromaDBSingleton()
        collection = chroma_db.get_or_create_collection()
    """

    _instance = None

    class _ChromaDB:
        def __init__(self):
            # Lots of different embedding functions are available.
            # https://docs.trychroma.com/embeddings
            # Embedding functions can be run on the CPU or GPU.
            # self.ef = embedding_functions.InstructorEmbeddingFunction()
            # self.ef = embedding_functions.InstructorEmbeddingFunction(
            #     model_name="hkunlp/instructor-xl", device="cuda")
            if settings.HUGGING_FACE_API_TOKEN:
                # BAAI/bge-base-en
                self.default_ef = embedding_functions.HuggingFaceEmbeddingFunction(
                    api_key=settings.HUGGING_FACE_API_TOKEN,
                    model_name="BAAI/bge-base-en",
                )
            else:
                # all-MiniLM-L6-v2
                self.default_ef = embedding_functions.DefaultEmbeddingFunction()

            self.default_ef = embedding_functions.DefaultEmbeddingFunction()

            self.client = chromadb.PersistentClient(path=settings.CHROMADB_PATH)

        def get_or_create_collection(
            self, name="default", embedding_function=None
        ) -> ChromaDBCollection:
            """
            Get or create a collection with the given name and embedding function.

            Args:
                name (str): Name of the collection.
                embedding_function: The embedding function for the collection.

            Returns:
                Collection: The obtained or created collection.
            """
            if embedding_function is None:
                embedding_function = self.default_ef
            return self.client.get_or_create_collection(
                name=name, embedding_function=embedding_function
            )

        def get_client(self):
            return self.client

    def __new__(cls):
        if not ChromaDBSingleton._instance:
            ChromaDBSingleton._instance = ChromaDBSingleton._ChromaDB()
        return ChromaDBSingleton._instance

    def __getattr__(self, name):
        return getattr(self._instance, name)

    def __setattr__(self, name, value):
        return setattr(self._instance, name, value)
