del C:\Users\mithi\AppData\Local\Temp\.model_server.pid
torch-model-archiver --model-name UNet --version 1.0 --model-file model.py --serialized-file 0_checkpoint.pt --handler handler.py --extra-files extrafiles.py
mv ./UNet.mar model-store/UNet.mar
torchserve --start --model-store ./model-store --models UNet=UNet.mar