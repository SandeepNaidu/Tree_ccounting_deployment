# del C:\Users\mithi\AppData\Local\Temp\.model_server.pid
torchserve --stop
rm logs/config/*.cfg
torch-model-archiver --model-name UNetMar --version 1.0 --model-file model.py --serialized-file 0_checkpoint.pt --handler handler.py --extra-files extrafiles.py -f --export-path ./model-store --runtime python3
torchserve --start --model-store ./model-store --models UNet=UNetMar.mar