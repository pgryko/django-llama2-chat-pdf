import uvicorn

# Used for pycharm development

if __name__ == "__main__":
    uvicorn.run(
        "server.asgi:application",
        reload=True,
        lifespan="off",
        reload_includes="*.html",
        workers=4,
    )
