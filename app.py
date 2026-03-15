from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(
        debug=False,
        host='0.0.0.0',
        port=5000
    )
    
    if is_desktop: # type: ignore
        # Desktop mode - disable auto-reload, use fixed port
        print("🖥️  Running in Desktop Mode")
        app.run(
            debug=False,
            host='127.0.0.1',
            port=5000,
            use_reloader=False
        )
    else:
        # Web mode - development server
        print("🌐 Running in Web Mode")
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000
        )