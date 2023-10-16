sudo docker build -t tcc-model .
sudo docker tag tcc-model:latest 320729208297.dkr.ecr.us-east-1.amazonaws.com/tcc-model:latest
sudo docker push 320729208297.dkr.ecr.us-east-1.amazonaws.com/tcc-model:latest
