clean:
	rm -rf src/__pycache__
	rm -rf src/__init__.py
	rm -rf src/modules/__pycache__
 
docker-build:
	docker build --rm=true -t [AWS_ACCOUNT_ID].dkr.ecr.ap-northeast-2.amazonaws.com/openlawdata-datapipeline-precnmsearch:latest .
 
docker-run:
	docker run --rm -it [AWS_ACCOUNT_ID].dkr.ecr.ap-northeast-2.amazonaws.com/openlawdata-datapipeline-precnmsearch:latest

docker-push: clean
	$$(aws ecr get-login --no-include-email --region ap-northeast-2)
	docker push [AWS_ACCOUNT_ID].dkr.ecr.ap-northeast-2.amazonaws.com/openlawdata-datapipeline-precnmsearch:latest