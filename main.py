import uvicorn

if __name__ == "__main__":
    # Bhai, ab bas 'python main.py' likh aur server chal jayega! 🚀
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8080,
        reload=True,  # Auto-reload jab bhi code change ho
    )
