clean:
	rm -rf src/__pycache__
	rm -rf src/__init__.py
	rm -rf src/modules/__pycache__
 
docker-build:
	docker-compose build
 
docker-run:
	docker-compose run --rm lambda src/lambda_function.lambda_handler