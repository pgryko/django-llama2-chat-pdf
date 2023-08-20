from ninja import NinjaAPI, Router


from server.auth import async_auth

from chat.apis.chat import router as chat_api
from chat.apis.conversation import router as conversation_api
from chat.apis.chroma import router as chroma_api


router = Router()

router.add_router("", chroma_api, tags=["chroma"])
router.add_router("", chat_api, tags=["chat"])
router.add_router("", conversation_api, tags=["conversation"])

api = NinjaAPI(
    title="Chat API",
    version="1.0.0",
    urls_namespace="chat-api",
    csrf=True,
    auth=async_auth,
)
