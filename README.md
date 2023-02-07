# Tree_ccounting_deployment


# checkpoint in aws

s3://aws-labeling/Tree_counting/0_checkpoint.pt

# for mar file generation

torch-model-archiver --model-name UNet --version 1.0 --model-file model.py --serialized-file 0_checkpoint.pt --handler handler.py --extra-files extrafiles.py

# cmd for torchserve start

torchserve --start --model-store ./models --models UNet=UNet.mar 

# for  inference

curl http://localhost:8080/predictions/UNet -T 71.jpg.JPG -o ouput.jpg

# source code

https://colab.research.google.com/drive/19DCJupRUivKyyL4ZZkJnj2KHdopXlwAP?usp=share_link

# checkpoint location in drive 

GET_AWS_DATA>UNet_results > saved outPuts > 0_checkpoint.pt

#My reference to write handler 

https://www.pento.ai/blog/custom-torchserve-handlers

https://gist.github.com/SrGrace/05e83d17825b0ef43cd4adc2f616027a
