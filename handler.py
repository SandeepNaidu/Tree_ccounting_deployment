import base64
import io
import os
import time
import cv2
import numpy as np
import torch
from PIL import Image
from torchvision.transforms import Compose
from ts.torch_handler.base_handler import BaseHandler
from extrafiles import Dataset_loader
from model import UNet
# from preprocessing import  split_image


class UNethandler(BaseHandler):

    def __init__(self):
        self._context = None
        self.initialized = False
        self.model = None
        self.device = None

    def initialize(self, context):
        """
        Invoke by torchserve for loading a model
        :param context: context contains model server system properties
        :return:
        """
        super().initialize(context)
        #  load the model
        self.manifest = context.manifest

        properties = context.system_properties
        model_dir = properties.get("model_dir")
        print("model_dir = ", model_dir)
        self.device = torch.device(
            "cuda:" + str(properties.get("gpu_id")) if torch.cuda.is_available() else "cpu")

        # Read model serialize/pt file
        serialized_file = self.manifest['model']['serializedFile']
        model_pt_path = os.path.join(model_dir, serialized_file)

        if not os.path.isfile(model_pt_path):
            raise RuntimeError("Missing the model.pt file")
        else:
            print("model_pt_path = ", model_pt_path)

        self.model = UNet(3, 2)
        # https://stackoverflow.com/questions/67000060/loading-model-failed-in-torchserving
        self.model.load_state_dict(
            torch.load(model_dir + '0_checkpoint.pt'))

        self.initialized = True

    def split_image(img, TARGET_SIZE):
        img_tiles = []

        for y in range(0, img.shape[0], TARGET_SIZE):
            for x in range(0, img.shape[1], TARGET_SIZE):
                img_tile = img[y:y + TARGET_SIZE, x:x + TARGET_SIZE]
                if img_tile.shape[0] == TARGET_SIZE and img_tile.shape[1] == TARGET_SIZE:
                    img_tiles.append(img_tile)

        return img_tiles

    def extract_output(model, data_path, save_path, device="cuda"):
        import torch.nn.functional as F
        model.eval()
        img_append = []
        for X in data_path:
            X = X.to(device)
            with torch.no_grad():
                y_pred = model(X)
                logits = F.softmax(y_pred, dim=1)
                aggr = torch.max(logits, dim=1)
                preds = aggr[1].cpu().numpy()  # .flatten()
                # print(preds.shape)
                img_batch = preds.shape[0]
                # print(preds[1][:][:].shape)
                for arr in range(0, img_batch):
                    img_tile = preds[arr][:][:]

                    # appending sub-image
                    if len(img_append) == 0:
                        img_append = img_tile
                    else:
                        img_append = np.append(img_append, img_tile, axis=1)

        return img_append

    def preprocess(self, image):
        print("preprocesed")
        img_tiles = self.split_image(image, 512)
        # extraction_set = Dataset_loader(img_tiles)
        # extraction_loader = DataLoader(
        # extraction_set, batch_size=16, shuffle=False, num_workers=2)
        print("preprocesed")
        return img_tiles

    def inference(self, model_input):
        extraction_set = Dataset_loader(model_input)
        extraction_loader = DataLoader(
            extraction_set, batch_size=16, shuffle=False, num_workers=2)

        appended_image = self.extract_output(
            self.model, extraction_loader, save_path=None, device=self.device)
        print("inferenced")
        return appended_image

    def repatch_image(appended_img, split_count):
        img_h_split = np.hsplit(appended_img, split_count)
        img_repatch = np.vstack(img_h_split)

        return img_repatch

    def postprocess(self, image, output, TARGET_SIZE):
        img_height = image.shape[0]
        img_width = image.shape[1]

        repatched_image = self.repatch_image(output, img_height // TARGET_SIZE)
        print("postprocesed")
        return repatched_image

    def load_images(self, data):
        images = []

        for row in data:
            # Compat layer: normally the envelope should just return the data
            # directly, but older versions of Torchserve didn't have envelope.
            image = row.get("data") or row.get("body")
            if isinstance(image, str):
                # if the image is a string of bytesarray.
                image = base64.b64decode(image)

            # the image is sent as bytesarray
            image = Image.open(io.BytesIO(image))
            images.append(image)

        return images

    def handle(self, data, context):

        data = self.load_images(data)

        print("PREPROCESS...")
        model_input = self.preprocess(data)

        print("INFERENCE...")
        model_output = self.inference(model_input)

        print("POSTPROCESS....")
        model_output = self.postprocess(data, model_output, 512)

        # cv2.imwrite('reult.png', model_output)

        return model_output
