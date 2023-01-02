# Tree_ccounting_deployment

#for mar file generation

torch-model-archiver --model-name UNet --version 1.0 --model-file model.py --serialized-file 0_checkpoint.pt --handler handler.py

#cmd for torchserve start

torchserve --start --model-store ./models --models UNet=UNet.mar 

#for  inference

curl http://localhost:8080/predictions/UNet -T 71.jpg.JPG -o ouput.jpg
