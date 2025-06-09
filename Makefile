run:
	conda run --no-capture-output -n qdii streamlit run src/pages/Index.py --server.port 8501

build:
	docker build -t qdii_data .
	
push:
	docker login
	docker buildx build --push -t kegao1995/qdii_data:latest .
pull:
	docker pull kegao1995/qdii_data:latest
	docker run --rm -d -p 8501:8501 kegao1995/qdii_data:latest