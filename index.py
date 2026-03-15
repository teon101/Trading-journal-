# Create index.py that imports your app
cat > index.py << 'EOF'
from run import app

# Vercel needs this
if __name__ == "__main__":
    app.run()
EOF