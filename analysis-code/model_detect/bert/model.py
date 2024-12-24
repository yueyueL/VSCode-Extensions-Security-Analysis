# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
import torch
import torch.nn as nn
import torch
from torch.autograd import Variable
import copy
from torch.nn import CrossEntropyLoss, MSELoss

    
    
class Model(nn.Module):   
    def __init__(self, encoder,config,tokenizer,args):
        super(Model, self).__init__()
        self.encoder = encoder
        self.config=config
        self.tokenizer=tokenizer
        self.args=args
    
    def forward(self, input_ids=None,labels=None): 
        outputs=self.encoder(input_ids,attention_mask=input_ids.ne(1))[0]
        logits=outputs
        prob=torch.nn.functional.softmax(logits, dim=-1) # change sigmoid to softmax
        if labels is not None:
            # Define the weights
            weights = torch.tensor([0.01, 0.1]).to("cuda:0") # adjust the values as needed
            loss_fct = CrossEntropyLoss(weight=weights) # use CrossEntropyLoss with class weights
            loss = loss_fct(logits.view(-1, self.config.num_labels), labels.view(-1))
            return loss,prob
        else:
            return prob        

