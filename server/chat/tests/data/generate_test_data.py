from typing import List

from chat.models import Conversation, Message as MessageModel

sample_conversation = [
    {
        "message_type": "SYSTEM",
        "content": "Use the following pieces of context to answer the users question. If you don't know the answer, just say that you don't know, don't try to make up an answer.",
        "updated_at": "2023-09-15T14:03:41.176Z",
    },
    {
        "message_type": "USER",
        "content": "Tell me about polish vat",
        "updated_at": "2023-09-15T14:03:41.177Z",
    },
    {
        "message_type": "CONTEXT",
        "content": "If you are registered for EU VAT and make purchases in Poland, you get PolishPolish VAT). \n \nYou can be registered for EU VAT only or for both: EU and Polish VAT.- each month you need to give back 23% VAT (PLN 23) to the Polish Tax \nOffice;VAT refund from the Polish Tax Office (if you are registered for both EU and \nPolish VAT).COSTS \n- Everything you buy in Poland is already VAT taxed. If you buy a pen for netpersons. \n \n \nEU VATbe deducted. This means you need to pay PLN 20.70 to the Polish Tax Office :within EU are VAT taxed by the company selling products or services.Je\u015bli jeste\u015b zarejestrowany do VATu EU i masz koszty w Polsce, to VAT PLpurchase; \n-  \nVAT CALCULATION",
        "updated_at": "2023-09-15T14:03:41.221Z",
    },
    {
        "message_type": "LLM",
        "content": ' Sure, I can help you with that!\n\nSo, it seems like you want to know more about Polish VAT, specifically how it works and what the requirements are for registering for it.\n\nFirstly, let\'s clarify that VAT stands for Value Added Tax, which is a consumption tax that is levied on goods and services within the European Union. In Poland, VAT is known as "VAT" or "VAT polski".\n\nIf you are registered for EU VAT and make purchases in Poland, you will need to pay Polish VAT, which is currently set at 23%. This means that for every PLN 100 spent, you will need to pay an additional PLN 23 in VAT.\n\nTo register for Polish VAT, you will need to have a valid EU VAT registration number. Once you are registered, you will need to file monthly VAT returns with the Polish Tax Office, and pay any VAT due on your purchases.\n\nIt\'s worth noting that if you are only registered for EU VAT, you will not be able to claim back any VAT paid on purchases made in Poland. However, if you are registered for both EU and Polish VAT, you may be eligible for a VAT refund from the Polish Tax Office.\n\nIn terms of costs, everything you buy in Poland is already VAT taxed, so you won\'t need to pay any additional VAT on top of the price you pay for the item. However, you may be able to deduct the VAT paid on business expenses, such as office supplies or travel expenses, when filing your VAT return.\n\nI hope this information helps! If you have any further questions about Polish VAT, feel free to ask.',
        "updated_at": "2023-09-15T14:04:16.441Z",
    },
    {
        "message_type": "SYSTEM",
        "content": "Use the following pieces of context to answer the users question. If you don't know the answer, just say that you don't know, don't try to make up an answer.",
        "updated_at": "2023-09-16T14:03:41.176Z",
    },
    {
        "message_type": "USER",
        "content": "Tell me about entropy",
        "updated_at": "2023-09-16T14:03:41.177Z",
    },
    {
        "message_type": "CONTEXT",
        "content": "Entropy and statistical thermodynamics are related",
        "updated_at": "2023-09-16T14:03:41.221Z",
    },
    {
        "message_type": "LLM",
        "content": "Sure, I can help you with that!\n\nSo, it seems like you want to know more about Entropy, "
        "specifically ... hope this information helps! If you have any further questions"
        "feel free to ask.",
        "updated_at": "2023-09-16T14:04:16.441Z",
    },
]


def load_conversations(conversation: Conversation) -> List[MessageModel]:
    messages = []

    for message in sample_conversation:
        message = MessageModel.objects.create(
            conversation=conversation,
            message_type=message["message_type"],
            content=message["content"],
            created_at=message["updated_at"],
            updated_at=message["updated_at"],
        )

        messages.append(message)

    return messages
