import os
import sys
import numpy as np
import torch
import torchvision.models
sys.modules['torchvision.models.utils'] = torch.hub  # Fix import errors for torch==1.10
from torchsr.models import ninasr_b0 as sr_model
from torchvision.transforms.functional import to_tensor



class SimpleSR:
    def __init__(self, target_resolution=(1920, 1080)):
        #os.environ["CUDA_VISIBLE_DEVICES"]=''
        self.target_resolution = target_resolution
        self.device = 'cpu'
        self.model = sr_model(scale=2, pretrained=True).to(self.device)


    def super_resolution(self, image: np.ndarray):
        #print(image.shape)
        with torch.no_grad():
            img = to_tensor(image).to(self.device).unsqueeze(0)
            out_image = self.model(img)
            out_image = out_image.detach().squeeze(0).permute(1, 2, 0).mul(255).clamp(0, 255)
            out_image = out_image.cpu().numpy().astype(np.uint8)

        print(out_image.shape)
        return out_image
