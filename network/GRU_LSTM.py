from ast import Raise
import os
import datetime
import random
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from Settings import *
from MiscFunctions import *
import time

MockData = False

class MyNet(nn.Module):
    def __init__(self, useGRU, DaysInData, hidden_dim, output_dim, n_layers, batchsize = 1, drop_prob=0.01):
        super(MyNet, self).__init__()
        SettingsObject = Settings(False)
        self.hidden_dim = hidden_dim
        self.n_layers = n_layers
        self.net_type = "GRU"
        self.batchsize = batchsize
        self.UseGRU = useGRU
        if self.UseGRU:
            #self.linear_input_dim_z= int(hidden_dim + input_dim_z) #Concat
            self.linear_input_dim_z= int(hidden_dim)
            self.gru = nn.GRU(DaysInData, hidden_dim, n_layers, batch_first=True, dropout=drop_prob)
        else:
            self.linear_input_dim_z= int(DaysInData*SettingsObject.trainingDataWindow)

        
        if MockData:
            self.fc0 = nn.Linear(self.linear_input_dim_z, self.linear_input_dim_z, bias=True)
            self.fc1 = nn.Linear(self.linear_input_dim_z,output_dim, bias=False)
        else:
            self.fc0 = nn.Linear(self.linear_input_dim_z, self.linear_input_dim_z, bias=True)
            self.fc1 = nn.Linear(self.linear_input_dim_z, int(self.linear_input_dim_z/4)+1, bias=False)
            self.fc2= nn.Linear(int(self.linear_input_dim_z /4)+1, int(self.linear_input_dim_z/8)+1, bias=False)
            self.fc3= nn.Linear(int(self.linear_input_dim_z /8)+1, output_dim, bias=False)
        
        self.relu = nn.Sigmoid()
        self.dropout= nn.Dropout(0.01)
        
        self.weights_initialization()
        
    def forward(self, data, h):
        if self.UseGRU:
            data, h = self.gru(data, h)
            data = data[:,-1]

        #out = self.dropout(out)
        if(MockData):
            
            data = self.fc0(self.relu(data))
            data = self.dropout(data)
            data = self.fc1(self.relu(data))
        else:
            data = self.fc0(self.relu(data))
            data = self.dropout(data)
            data = self.fc1(self.relu(data))
            data = self.fc2(self.relu(data))
            data = self.fc3(self.relu(data))
        
        return data, h
    
    def init_hidden(self):
        weight = next(self.parameters()).data
        hidden = weight.new(self.n_layers, self.batchsize, self.hidden_dim).zero_()
        return hidden

    def weights_initialization(self):
            '''
            When we define all the modules such as the layers in '__init__()'
            method above, these are all stored in 'self.modules()'.
            We go through each module one by one. This is the entire network,
            basically.
            '''
            
            SettingsObject = Settings(False)
            
            
            for m in self.modules():
                if(self.net_type == 'GRU'):
                    if isinstance(m, nn.Linear):
                        m.weight.data.uniform_(SettingsObject.weightlimit_low, SettingsObject.weightlimit_high)
                        
                        if(m.bias != None):
                            m.bias.data.uniform_(SettingsObject.bias_low, SettingsObject.bias_high)  
                
                elif(self.net_type == 'CONV3D'):
                    if isinstance(m, nn.Linear):
                        m.weight.fill_(random.uniform(SettingsObject.weightlimit_high,SettingsObject.weightlimit_low))
                        if(m.bias != None):
                            m.bias.data.fill_(random.uniform(SettingsObject.bias_high,SettingsObject.bias_low))
                            
                elif(self.net_type == 'LSTM'):
                    if isinstance(m, nn.Linear):
                        m.weight.data.uniform_(SettingsObject.weightlimit_low, SettingsObject.weightlimit_high)
                        if(m.bias != None):
                            m.bias.data.uniform_(SettingsObject.bias_low, SettingsObject.bias_high) 

def prepare_data(TargetStock_index_array):  
    
    x = []
    z = []
    SettingsObject = Settings(False)
    
    if MockData:
        print(f'doing mock data.....')   
        TargetStock_index_array =[0]     
        SettingsObject.PredictionPart = 0.3 
        x = [[1, 1.61, 2.45, 3.42, 4.42, 5.33, 6.07, 6.54, 6.71, 6.54, 6.07, 5.33, 4.42, 3.42, 2.45, 1.61, 1.00, 0.68, 0.68, 1.00, 1.61, 2.45, 3.42, 4.42, 5.33, 6.07, 6.54, 6.71, 6.54, 6.07, 5.33, 4.42, 3.42, 2.45, 1.61, 1.00, 0.68, 0.68, 1.00, 1.61, 2.45, 3.42, 4.42, 5.33, 6.07, 6.54, 6.71, 6.54, 6.07, 5.33],
            [1.03, 1.67, 2.53, 3.53, 4.56, 5.51, 6.27, 6.76, 6.93, 6.76, 6.27, 5.51, 4.56, 3.53, 2.53, 1.67, 1.03, 0.70, 0.70, 1.03, 1.67, 2.53, 3.53, 4.56, 5.51, 6.27, 6.76, 6.93, 6.76, 6.27, 5.51, 4.56, 3.53, 2.53, 1.67, 1.03, 0.70, 0.70, 1.03, 1.67, 2.53, 3.53, 4.56, 5.51, 6.27, 6.76, 6.93, 6.76, 6.27, 5.51],
            [1.10, 1.77, 2.69, 3.75, 4.84, 5.84, 6.65, 7.17, 7.35, 7.17, 6.65, 5.84, 4.84, 3.75, 2.69, 1.77, 1.10, 0.74, 0.74, 1.10, 1.77, 2.69, 3.75, 4.84, 5.84, 6.65, 7.17, 7.35, 7.17, 6.65, 5.84, 4.84, 3.75, 2.69, 1.77, 1.10, 0.74, 0.74, 1.10, 1.77, 2.69, 3.75, 4.84, 5.84, 6.65, 7.17, 7.35, 7.17, 6.65, 5.84],
            [1.19, 1.92, 2.91, 4.06, 5.25, 6.33, 7.21, 7.77, 7.97, 7.77, 7.21, 6.33, 5.25, 4.06, 2.91, 1.92, 1.19, 0.80, 0.80, 1.19, 1.92, 2.91, 4.06, 5.25, 6.33, 7.21, 7.77, 7.97, 7.77, 7.21, 6.33, 5.25, 4.06, 2.91, 1.92, 1.19, 0.80, 0.80, 1.19, 1.92, 2.91, 4.06, 5.25, 6.33, 7.21, 7.77, 7.97, 7.77, 7.21, 6.33],
            [1.30, 2.10, 3.19, 4.46, 5.75, 6.95, 7.91, 8.53, 8.74, 8.53, 7.91, 6.95, 5.75, 4.46, 3.19, 2.10, 1.30, 0.88, 0.88, 1.30, 2.10, 3.19, 4.46, 5.75, 6.95, 7.91, 8.53, 8.74, 8.53, 7.91, 6.95, 5.75, 4.46, 3.19, 2.10, 1.30, 0.88, 0.88, 1.30, 2.10, 3.19, 4.46, 5.75, 6.95, 7.91, 8.53, 8.74, 8.53, 7.91, 6.95],
            [1.43, 2.31, 3.51, 4.90, 6.33, 7.64, 8.69, 9.38, 9.61, 9.38, 8.69, 7.64, 6.33, 4.90, 3.51, 2.31, 1.43, 0.97, 0.97, 1.43, 2.31, 3.51, 4.90, 6.33, 7.64, 8.69, 9.38, 9.61, 9.38, 8.69, 7.64, 6.33, 4.90, 3.51, 2.31, 1.43, 0.97, 0.97, 1.43, 2.31, 3.51, 4.90, 6.33, 7.64, 8.69, 9.38, 9.61, 9.38, 8.69, 7.64],
            [1.56, 2.52, 3.83, 5.35, 6.91, 8.34, 9.49, 10.23, 10.49, 10.23, 9.49, 8.34, 6.91, 5.35, 3.83, 2.52, 1.56, 1.06, 1.06, 1.56, 2.52, 3.83, 5.35, 6.91, 8.34, 9.49, 10.23, 10.49, 10.23, 9.49, 8.34, 6.91, 5.35, 3.83, 2.52, 1.56, 1.06, 1.06, 1.56, 2.52, 3.83, 5.35, 6.91, 8.34, 9.49, 10.23, 10.49, 10.23, 9.49, 8.34],
            [1.68, 2.71, 4.12, 5.74, 7.42, 8.95, 10.19, 10.99, 11.26, 10.99, 10.19, 8.95, 7.42, 5.74, 4.12, 2.71, 1.68, 1.13, 1.13, 1.68, 2.71, 4.12, 5.74, 7.42, 8.95, 10.19, 10.99, 11.26, 10.99, 10.19, 8.95, 7.42, 5.74, 4.12, 2.71, 1.68, 1.13, 1.13, 1.68, 2.71, 4.12, 5.74, 7.42, 8.95, 10.19, 10.99, 11.26, 10.99, 10.19, 8.95],
            [1.76, 2.84, 4.31, 6.02, 7.77, 9.38, 10.67, 11.51, 11.80, 11.51, 10.67, 9.38, 7.77, 6.02, 4.31, 2.84, 1.76, 1.19, 1.19, 1.76, 2.84, 4.31, 6.02, 7.77, 9.38, 10.67, 11.51, 11.80, 11.51, 10.67, 9.38, 7.77, 6.02, 4.31, 2.84, 1.76, 1.19, 1.19, 1.76, 2.84, 4.31, 6.02, 7.77, 9.38, 10.67, 11.51, 11.80, 11.51, 10.67, 9.38],
            [1.79, 2.89, 4.38, 6.12, 7.90, 9.53, 10.85, 11.70, 11.99, 11.70, 10.85, 9.53, 7.90, 6.12, 4.38, 2.89, 1.79, 1.21, 1.21, 1.79, 2.89, 4.38, 6.12, 7.90, 9.53, 10.85, 11.70, 11.99, 11.70, 10.85, 9.53, 7.90, 6.12, 4.38, 2.89, 1.79, 1.21, 1.21, 1.79, 2.89, 4.38, 6.12, 7.90, 9.53, 10.85, 11.70, 11.99, 11.70, 10.85, 9.53],
            [1.76, 2.84, 4.31, 6.01, 7.77, 9.38, 10.67, 11.51, 11.80, 11.51, 10.67, 9.38, 7.77, 6.01, 4.31, 2.84, 1.76, 1.19, 1.19, 1.76, 2.84, 4.31, 6.01, 7.77, 9.38, 10.67, 11.51, 11.80, 11.51, 10.67, 9.38, 7.77, 6.01, 4.31, 2.84, 1.76, 1.19, 1.19, 1.76, 2.84, 4.31, 6.01, 7.77, 9.38, 10.67, 11.51, 11.80, 11.51, 10.67, 9.38],
            [1.67, 2.70, 4.11, 5.73, 7.40, 8.93, 10.16, 10.96, 11.24, 10.96, 10.16, 8.93, 7.40, 5.73, 4.11, 2.70, 1.67, 1.13, 1.13, 1.67, 2.70, 4.11, 5.73, 7.40, 8.93, 10.16, 10.96, 11.24, 10.96, 10.16, 8.93, 7.40, 5.73, 4.11, 2.70, 1.67, 1.13, 1.13, 1.67, 2.70, 4.11, 5.73, 7.40, 8.93, 10.16, 10.96, 11.24, 10.96, 10.16, 8.93],
            [1.55, 2.50, 3.80, 5.31, 6.85, 8.27, 9.42, 10.15, 10.41, 10.15, 9.42, 8.27, 6.85, 5.31, 3.80, 2.50, 1.55, 1.05, 1.05, 1.55, 2.50, 3.80, 5.31, 6.85, 8.27, 9.42, 10.15, 10.41, 10.15, 9.42, 8.27, 6.85, 5.31, 3.80, 2.50, 1.55, 1.05, 1.05, 1.55, 2.50, 3.80, 5.31, 6.85, 8.27, 9.42, 10.15, 10.41, 10.15, 9.42, 8.27],
            [1.41, 2.27, 3.45, 4.82, 6.23, 7.52, 8.55, 9.22, 9.46, 9.22, 8.55, 7.52, 6.23, 4.82, 3.45, 2.27, 1.41, 0.95, 0.95, 1.41, 2.27, 3.45, 4.82, 6.23, 7.52, 8.55, 9.22, 9.46, 9.22, 8.55, 7.52, 6.23, 4.82, 3.45, 2.27, 1.41, 0.95, 0.95, 1.41, 2.27, 3.45, 4.82, 6.23, 7.52, 8.55, 9.22, 9.46, 9.22, 8.55, 7.52],
            [1.27, 2.05, 3.11, 4.34, 5.60, 6.77, 7.70, 8.30, 8.51, 8.30, 7.70, 6.77, 5.60, 4.34, 3.11, 2.05, 1.27, 0.86, 0.86, 1.27, 2.05, 3.11, 4.34, 5.60, 6.77, 7.70, 8.30, 8.51, 8.30, 7.70, 6.77, 5.60, 4.34, 3.11, 2.05, 1.27, 0.86, 0.86, 1.27, 2.05, 3.11, 4.34, 5.60, 6.77, 7.70, 8.30, 8.51, 8.30, 7.70, 6.77],
            [1.15, 1.85, 2.81, 3.92, 5.06, 6.11, 6.95, 7.50, 7.69, 7.50, 6.95, 6.11, 5.06, 3.92, 2.81, 1.85, 1.15, 0.77, 0.77, 1.15, 1.85, 2.81, 3.92, 5.06, 6.11, 6.95, 7.50, 7.69, 7.50, 6.95, 6.11, 5.06, 3.92, 2.81, 1.85, 1.15, 0.77, 0.77, 1.15, 1.85, 2.81, 3.92, 5.06, 6.11, 6.95, 7.50, 7.69, 7.50, 6.95, 6.11],
            [1.05, 1.69, 2.57, 3.59, 4.64, 5.60, 6.37, 6.87, 7.04, 6.87, 6.37, 5.60, 4.64, 3.59, 2.57, 1.69, 1.05, 0.71, 0.71, 1.05, 1.69, 2.57, 3.59, 4.64, 5.60, 6.37, 6.87, 7.04, 6.87, 6.37, 5.60, 4.64, 3.59, 2.57, 1.69, 1.05, 0.71, 0.71, 1.05, 1.69, 2.57, 3.59, 4.64, 5.60, 6.37, 6.87, 7.04, 6.87, 6.37, 5.60],
            [0.99, 1.59, 2.42, 3.37, 4.35, 5.26, 5.98, 6.45, 6.61, 6.45, 5.98, 5.26, 4.35, 3.37, 2.42, 1.59, 0.99, 0.67, 0.67, 0.99, 1.59, 2.42, 3.37, 4.35, 5.26, 5.98, 6.45, 6.61, 6.45, 5.98, 5.26, 4.35, 3.37, 2.42, 1.59, 0.99, 0.67, 0.67, 0.99, 1.59, 2.42, 3.37, 4.35, 5.26, 5.98, 6.45, 6.61, 6.45, 5.98, 5.26],
            [0.95, 1.54, 2.34, 3.26, 4.21, 5.08, 5.79, 6.24, 6.40, 6.24, 5.79, 5.08, 4.21, 3.26, 2.34, 1.54, 0.95, 0.64, 0.64, 0.95, 1.54, 2.34, 3.26, 4.21, 5.08, 5.79, 6.24, 6.40, 6.24, 5.79, 5.08, 4.21, 3.26, 2.34, 1.54, 0.95, 0.64, 0.64, 0.95, 1.54, 2.34, 3.26, 4.21, 5.08, 5.79, 6.24, 6.40, 6.24, 5.79, 5.08],
            [1, 1.61, 2.45, 3.42, 4.42, 5.33, 6.07, 6.54, 6.71, 6.54, 6.07, 5.33, 4.42, 3.42, 2.45, 1.61, 1.00, 0.68, 0.68, 1.00, 1.61, 2.45, 3.42, 4.42, 5.33, 6.07, 6.54, 6.71, 6.54, 6.07, 5.33, 4.42, 3.42, 2.45, 1.61, 1.00, 0.68, 0.68, 1.00, 1.61, 2.45, 3.42, 4.42, 5.33, 6.07, 6.54, 6.71, 6.54, 6.07, 5.33],
            [1.03, 1.67, 2.53, 3.53, 4.56, 5.51, 6.27, 6.76, 6.93, 6.76, 6.27, 5.51, 4.56, 3.53, 2.53, 1.67, 1.03, 0.70, 0.70, 1.03, 1.67, 2.53, 3.53, 4.56, 5.51, 6.27, 6.76, 6.93, 6.76, 6.27, 5.51, 4.56, 3.53, 2.53, 1.67, 1.03, 0.70, 0.70, 1.03, 1.67, 2.53, 3.53, 4.56, 5.51, 6.27, 6.76, 6.93, 6.76, 6.27, 5.51],
            [1.10, 1.77, 2.69, 3.75, 4.84, 5.84, 6.65, 7.17, 7.35, 7.17, 6.65, 5.84, 4.84, 3.75, 2.69, 1.77, 1.10, 0.74, 0.74, 1.10, 1.77, 2.69, 3.75, 4.84, 5.84, 6.65, 7.17, 7.35, 7.17, 6.65, 5.84, 4.84, 3.75, 2.69, 1.77, 1.10, 0.74, 0.74, 1.10, 1.77, 2.69, 3.75, 4.84, 5.84, 6.65, 7.17, 7.35, 7.17, 6.65, 5.84],
            [1.19, 1.92, 2.91, 4.06, 5.25, 6.33, 7.21, 7.77, 7.97, 7.77, 7.21, 6.33, 5.25, 4.06, 2.91, 1.92, 1.19, 0.80, 0.80, 1.19, 1.92, 2.91, 4.06, 5.25, 6.33, 7.21, 7.77, 7.97, 7.77, 7.21, 6.33, 5.25, 4.06, 2.91, 1.92, 1.19, 0.80, 0.80, 1.19, 1.92, 2.91, 4.06, 5.25, 6.33, 7.21, 7.77, 7.97, 7.77, 7.21, 6.33],
            [1.30, 2.10, 3.19, 4.46, 5.75, 6.95, 7.91, 8.53, 8.74, 8.53, 7.91, 6.95, 5.75, 4.46, 3.19, 2.10, 1.30, 0.88, 0.88, 1.30, 2.10, 3.19, 4.46, 5.75, 6.95, 7.91, 8.53, 8.74, 8.53, 7.91, 6.95, 5.75, 4.46, 3.19, 2.10, 1.30, 0.88, 0.88, 1.30, 2.10, 3.19, 4.46, 5.75, 6.95, 7.91, 8.53, 8.74, 8.53, 7.91, 6.95],
            [1.43, 2.31, 3.51, 4.90, 6.33, 7.64, 8.69, 9.38, 9.61, 9.38, 8.69, 7.64, 6.33, 4.90, 3.51, 2.31, 1.43, 0.97, 0.97, 1.43, 2.31, 3.51, 4.90, 6.33, 7.64, 8.69, 9.38, 9.61, 9.38, 8.69, 7.64, 6.33, 4.90, 3.51, 2.31, 1.43, 0.97, 0.97, 1.43, 2.31, 3.51, 4.90, 6.33, 7.64, 8.69, 9.38, 9.61, 9.38, 8.69, 7.64],
            [1.56, 2.52, 3.83, 5.35, 6.91, 8.34, 9.49, 10.23, 10.49, 10.23, 9.49, 8.34, 6.91, 5.35, 3.83, 2.52, 1.56, 1.06, 1.06, 1.56, 2.52, 3.83, 5.35, 6.91, 8.34, 9.49, 10.23, 10.49, 10.23, 9.49, 8.34, 6.91, 5.35, 3.83, 2.52, 1.56, 1.06, 1.06, 1.56, 2.52, 3.83, 5.35, 6.91, 8.34, 9.49, 10.23, 10.49, 10.23, 9.49, 8.34],
            [1.68, 2.71, 4.12, 5.74, 7.42, 8.95, 10.19, 10.99, 11.26, 10.99, 10.19, 8.95, 7.42, 5.74, 4.12, 2.71, 1.68, 1.13, 1.13, 1.68, 2.71, 4.12, 5.74, 7.42, 8.95, 10.19, 10.99, 11.26, 10.99, 10.19, 8.95, 7.42, 5.74, 4.12, 2.71, 1.68, 1.13, 1.13, 1.68, 2.71, 4.12, 5.74, 7.42, 8.95, 10.19, 10.99, 11.26, 10.99, 10.19, 8.95],
            [1.76, 2.84, 4.31, 6.02, 7.77, 9.38, 10.67, 11.51, 11.80, 11.51, 10.67, 9.38, 7.77, 6.02, 4.31, 2.84, 1.76, 1.19, 1.19, 1.76, 2.84, 4.31, 6.02, 7.77, 9.38, 10.67, 11.51, 11.80, 11.51, 10.67, 9.38, 7.77, 6.02, 4.31, 2.84, 1.76, 1.19, 1.19, 1.76, 2.84, 4.31, 6.02, 7.77, 9.38, 10.67, 11.51, 11.80, 11.51, 10.67, 9.38],
            [1.79, 2.89, 4.38, 6.12, 7.90, 9.53, 10.85, 11.70, 11.99, 11.70, 10.85, 9.53, 7.90, 6.12, 4.38, 2.89, 1.79, 1.21, 1.21, 1.79, 2.89, 4.38, 6.12, 7.90, 9.53, 10.85, 11.70, 11.99, 11.70, 10.85, 9.53, 7.90, 6.12, 4.38, 2.89, 1.79, 1.21, 1.21, 1.79, 2.89, 4.38, 6.12, 7.90, 9.53, 10.85, 11.70, 11.99, 11.70, 10.85, 9.53],
            [1.76, 2.84, 4.31, 6.01, 7.77, 9.38, 10.67, 11.51, 11.80, 11.51, 10.67, 9.38, 7.77, 6.01, 4.31, 2.84, 1.76, 1.19, 1.19, 1.76, 2.84, 4.31, 6.01, 7.77, 9.38, 10.67, 11.51, 11.80, 11.51, 10.67, 9.38, 7.77, 6.01, 4.31, 2.84, 1.76, 1.19, 1.19, 1.76, 2.84, 4.31, 6.01, 7.77, 9.38, 10.67, 11.51, 11.80, 11.51, 10.67, 9.38],
            [1.67, 2.70, 4.11, 5.73, 7.40, 8.93, 10.16, 10.96, 11.24, 10.96, 10.16, 8.93, 7.40, 5.73, 4.11, 2.70, 1.67, 1.13, 1.13, 1.67, 2.70, 4.11, 5.73, 7.40, 8.93, 10.16, 10.96, 11.24, 10.96, 10.16, 8.93, 7.40, 5.73, 4.11, 2.70, 1.67, 1.13, 1.13, 1.67, 2.70, 4.11, 5.73, 7.40, 8.93, 10.16, 10.96, 11.24, 10.96, 10.16, 8.93],
            [1.55, 2.50, 3.80, 5.31, 6.85, 8.27, 9.42, 10.15, 10.41, 10.15, 9.42, 8.27, 6.85, 5.31, 3.80, 2.50, 1.55, 1.05, 1.05, 1.55, 2.50, 3.80, 5.31, 6.85, 8.27, 9.42, 10.15, 10.41, 10.15, 9.42, 8.27, 6.85, 5.31, 3.80, 2.50, 1.55, 1.05, 1.05, 1.55, 2.50, 3.80, 5.31, 6.85, 8.27, 9.42, 10.15, 10.41, 10.15, 9.42, 8.27],
            [1.41, 2.27, 3.45, 4.82, 6.23, 7.52, 8.55, 9.22, 9.46, 9.22, 8.55, 7.52, 6.23, 4.82, 3.45, 2.27, 1.41, 0.95, 0.95, 1.41, 2.27, 3.45, 4.82, 6.23, 7.52, 8.55, 9.22, 9.46, 9.22, 8.55, 7.52, 6.23, 4.82, 3.45, 2.27, 1.41, 0.95, 0.95, 1.41, 2.27, 3.45, 4.82, 6.23, 7.52, 8.55, 9.22, 9.46, 9.22, 8.55, 7.52],
            [1.27, 2.05, 3.11, 4.34, 5.60, 6.77, 7.70, 8.30, 8.51, 8.30, 7.70, 6.77, 5.60, 4.34, 3.11, 2.05, 1.27, 0.86, 0.86, 1.27, 2.05, 3.11, 4.34, 5.60, 6.77, 7.70, 8.30, 8.51, 8.30, 7.70, 6.77, 5.60, 4.34, 3.11, 2.05, 1.27, 0.86, 0.86, 1.27, 2.05, 3.11, 4.34, 5.60, 6.77, 7.70, 8.30, 8.51, 8.30, 7.70, 6.77],
            [1.15, 1.85, 2.81, 3.92, 5.06, 6.11, 6.95, 7.50, 7.69, 7.50, 6.95, 6.11, 5.06, 3.92, 2.81, 1.85, 1.15, 0.77, 0.77, 1.15, 1.85, 2.81, 3.92, 5.06, 6.11, 6.95, 7.50, 7.69, 7.50, 6.95, 6.11, 5.06, 3.92, 2.81, 1.85, 1.15, 0.77, 0.77, 1.15, 1.85, 2.81, 3.92, 5.06, 6.11, 6.95, 7.50, 7.69, 7.50, 6.95, 6.11],
            [1.05, 1.69, 2.57, 3.59, 4.64, 5.60, 6.37, 6.87, 7.04, 6.87, 6.37, 5.60, 4.64, 3.59, 2.57, 1.69, 1.05, 0.71, 0.71, 1.05, 1.69, 2.57, 3.59, 4.64, 5.60, 6.37, 6.87, 7.04, 6.87, 6.37, 5.60, 4.64, 3.59, 2.57, 1.69, 1.05, 0.71, 0.71, 1.05, 1.69, 2.57, 3.59, 4.64, 5.60, 6.37, 6.87, 7.04, 6.87, 6.37, 5.60],
            [0.99, 1.59, 2.42, 3.37, 4.35, 5.26, 5.98, 6.45, 6.61, 6.45, 5.98, 5.26, 4.35, 3.37, 2.42, 1.59, 0.99, 0.67, 0.67, 0.99, 1.59, 2.42, 3.37, 4.35, 5.26, 5.98, 6.45, 6.61, 6.45, 5.98, 5.26, 4.35, 3.37, 2.42, 1.59, 0.99, 0.67, 0.67, 0.99, 1.59, 2.42, 3.37, 4.35, 5.26, 5.98, 6.45, 6.61, 6.45, 5.98, 5.26],
            [0.95, 1.54, 2.34, 3.26, 4.21, 5.08, 5.79, 6.24, 6.40, 6.24, 5.79, 5.08, 4.21, 3.26, 2.34, 1.54, 0.95, 0.64, 0.64, 0.95, 1.54, 2.34, 3.26, 4.21, 5.08, 5.79, 6.24, 6.40, 6.24, 5.79, 5.08, 4.21, 3.26, 2.34, 1.54, 0.95, 0.64, 0.64, 0.95, 1.54, 2.34, 3.26, 4.21, 5.08, 5.79, 6.24, 6.40, 6.24, 5.79, 5.08],
            [1, 1.61, 2.45, 3.42, 4.42, 5.33, 6.07, 6.54, 6.71, 6.54, 6.07, 5.33, 4.42, 3.42, 2.45, 1.61, 1.00, 0.68, 0.68, 1.00, 1.61, 2.45, 3.42, 4.42, 5.33, 6.07, 6.54, 6.71, 6.54, 6.07, 5.33, 4.42, 3.42, 2.45, 1.61, 1.00, 0.68, 0.68, 1.00, 1.61, 2.45, 3.42, 4.42, 5.33, 6.07, 6.54, 6.71, 6.54, 6.07, 5.33],
            [1.03, 1.67, 2.53, 3.53, 4.56, 5.51, 6.27, 6.76, 6.93, 6.76, 6.27, 5.51, 4.56, 3.53, 2.53, 1.67, 1.03, 0.70, 0.70, 1.03, 1.67, 2.53, 3.53, 4.56, 5.51, 6.27, 6.76, 6.93, 6.76, 6.27, 5.51, 4.56, 3.53, 2.53, 1.67, 1.03, 0.70, 0.70, 1.03, 1.67, 2.53, 3.53, 4.56, 5.51, 6.27, 6.76, 6.93, 6.76, 6.27, 5.51],
            [1.10, 1.77, 2.69, 3.75, 4.84, 5.84, 6.65, 7.17, 7.35, 7.17, 6.65, 5.84, 4.84, 3.75, 2.69, 1.77, 1.10, 0.74, 0.74, 1.10, 1.77, 2.69, 3.75, 4.84, 5.84, 6.65, 7.17, 7.35, 7.17, 6.65, 5.84, 4.84, 3.75, 2.69, 1.77, 1.10, 0.74, 0.74, 1.10, 1.77, 2.69, 3.75, 4.84, 5.84, 6.65, 7.17, 7.35, 7.17, 6.65, 5.84],
            [1.19, 1.92, 2.91, 4.06, 5.25, 6.33, 7.21, 7.77, 7.97, 7.77, 7.21, 6.33, 5.25, 4.06, 2.91, 1.92, 1.19, 0.80, 0.80, 1.19, 1.92, 2.91, 4.06, 5.25, 6.33, 7.21, 7.77, 7.97, 7.77, 7.21, 6.33, 5.25, 4.06, 2.91, 1.92, 1.19, 0.80, 0.80, 1.19, 1.92, 2.91, 4.06, 5.25, 6.33, 7.21, 7.77, 7.97, 7.77, 7.21, 6.33],
            [1.30, 2.10, 3.19, 4.46, 5.75, 6.95, 7.91, 8.53, 8.74, 8.53, 7.91, 6.95, 5.75, 4.46, 3.19, 2.10, 1.30, 0.88, 0.88, 1.30, 2.10, 3.19, 4.46, 5.75, 6.95, 7.91, 8.53, 8.74, 8.53, 7.91, 6.95, 5.75, 4.46, 3.19, 2.10, 1.30, 0.88, 0.88, 1.30, 2.10, 3.19, 4.46, 5.75, 6.95, 7.91, 8.53, 8.74, 8.53, 7.91, 6.95],
            [1.43, 2.31, 3.51, 4.90, 6.33, 7.64, 8.69, 9.38, 9.61, 9.38, 8.69, 7.64, 6.33, 4.90, 3.51, 2.31, 1.43, 0.97, 0.97, 1.43, 2.31, 3.51, 4.90, 6.33, 7.64, 8.69, 9.38, 9.61, 9.38, 8.69, 7.64, 6.33, 4.90, 3.51, 2.31, 1.43, 0.97, 0.97, 1.43, 2.31, 3.51, 4.90, 6.33, 7.64, 8.69, 9.38, 9.61, 9.38, 8.69, 7.64],
            [1.56, 2.52, 3.83, 5.35, 6.91, 8.34, 9.49, 10.23, 10.49, 10.23, 9.49, 8.34, 6.91, 5.35, 3.83, 2.52, 1.56, 1.06, 1.06, 1.56, 2.52, 3.83, 5.35, 6.91, 8.34, 9.49, 10.23, 10.49, 10.23, 9.49, 8.34, 6.91, 5.35, 3.83, 2.52, 1.56, 1.06, 1.06, 1.56, 2.52, 3.83, 5.35, 6.91, 8.34, 9.49, 10.23, 10.49, 10.23, 9.49, 8.34],
            [1.68, 2.71, 4.12, 5.74, 7.42, 8.95, 10.19, 10.99, 11.26, 10.99, 10.19, 8.95, 7.42, 5.74, 4.12, 2.71, 1.68, 1.13, 1.13, 1.68, 2.71, 4.12, 5.74, 7.42, 8.95, 10.19, 10.99, 11.26, 10.99, 10.19, 8.95, 7.42, 5.74, 4.12, 2.71, 1.68, 1.13, 1.13, 1.68, 2.71, 4.12, 5.74, 7.42, 8.95, 10.19, 10.99, 11.26, 10.99, 10.19, 8.95],
            [1.76, 2.84, 4.31, 6.02, 7.77, 9.38, 10.67, 11.51, 11.80, 11.51, 10.67, 9.38, 7.77, 6.02, 4.31, 2.84, 1.76, 1.19, 1.19, 1.76, 2.84, 4.31, 6.02, 7.77, 9.38, 10.67, 11.51, 11.80, 11.51, 10.67, 9.38, 7.77, 6.02, 4.31, 2.84, 1.76, 1.19, 1.19, 1.76, 2.84, 4.31, 6.02, 7.77, 9.38, 10.67, 11.51, 11.80, 11.51, 10.67, 9.38],
            [1.79, 2.89, 4.38, 6.12, 7.90, 9.53, 10.85, 11.70, 11.99, 11.70, 10.85, 9.53, 7.90, 6.12, 4.38, 2.89, 1.79, 1.21, 1.21, 1.79, 2.89, 4.38, 6.12, 7.90, 9.53, 10.85, 11.70, 11.99, 11.70, 10.85, 9.53, 7.90, 6.12, 4.38, 2.89, 1.79, 1.21, 1.21, 1.79, 2.89, 4.38, 6.12, 7.90, 9.53, 10.85, 11.70, 11.99, 11.70, 10.85, 9.53],
            [1.76, 2.84, 4.31, 6.01, 7.77, 9.38, 10.67, 11.51, 11.80, 11.51, 10.67, 9.38, 7.77, 6.01, 4.31, 2.84, 1.76, 1.19, 1.19, 1.76, 2.84, 4.31, 6.01, 7.77, 9.38, 10.67, 11.51, 11.80, 11.51, 10.67, 9.38, 7.77, 6.01, 4.31, 2.84, 1.76, 1.19, 1.19, 1.76, 2.84, 4.31, 6.01, 7.77, 9.38, 10.67, 11.51, 11.80, 11.51, 10.67, 9.38],
            [1.67, 2.70, 4.11, 5.73, 7.40, 8.93, 10.16, 10.96, 11.24, 10.96, 10.16, 8.93, 7.40, 5.73, 4.11, 2.70, 1.67, 1.13, 1.13, 1.67, 2.70, 4.11, 5.73, 7.40, 8.93, 10.16, 10.96, 11.24, 10.96, 10.16, 8.93, 7.40, 5.73, 4.11, 2.70, 1.67, 1.13, 1.13, 1.67, 2.70, 4.11, 5.73, 7.40, 8.93, 10.16, 10.96, 11.24, 10.96, 10.16, 8.93],
            [1.55, 2.50, 3.80, 5.31, 6.85, 8.27, 9.42, 10.15, 10.41, 10.15, 9.42, 8.27, 6.85, 5.31, 3.80, 2.50, 1.55, 1.05, 1.05, 1.55, 2.50, 3.80, 5.31, 6.85, 8.27, 9.42, 10.15, 10.41, 10.15, 9.42, 8.27, 6.85, 5.31, 3.80, 2.50, 1.55, 1.05, 1.05, 1.55, 2.50, 3.80, 5.31, 6.85, 8.27, 9.42, 10.15, 10.41, 10.15, 9.42, 8.27],
            [1.41, 2.27, 3.45, 4.82, 6.23, 7.52, 8.55, 9.22, 9.46, 9.22, 8.55, 7.52, 6.23, 4.82, 3.45, 2.27, 1.41, 0.95, 0.95, 1.41, 2.27, 3.45, 4.82, 6.23, 7.52, 8.55, 9.22, 9.46, 9.22, 8.55, 7.52, 6.23, 4.82, 3.45, 2.27, 1.41, 0.95, 0.95, 1.41, 2.27, 3.45, 4.82, 6.23, 7.52, 8.55, 9.22, 9.46, 9.22, 8.55, 7.52],
            [1.27, 2.05, 3.11, 4.34, 5.60, 6.77, 7.70, 8.30, 8.51, 8.30, 7.70, 6.77, 5.60, 4.34, 3.11, 2.05, 1.27, 0.86, 0.86, 1.27, 2.05, 3.11, 4.34, 5.60, 6.77, 7.70, 8.30, 8.51, 8.30, 7.70, 6.77, 5.60, 4.34, 3.11, 2.05, 1.27, 0.86, 0.86, 1.27, 2.05, 3.11, 4.34, 5.60, 6.77, 7.70, 8.30, 8.51, 8.30, 7.70, 6.77],
            [1.15, 1.85, 2.81, 3.92, 5.06, 6.11, 6.95, 7.50, 7.69, 7.50, 6.95, 6.11, 5.06, 3.92, 2.81, 1.85, 1.15, 0.77, 0.77, 1.15, 1.85, 2.81, 3.92, 5.06, 6.11, 6.95, 7.50, 7.69, 7.50, 6.95, 6.11, 5.06, 3.92, 2.81, 1.85, 1.15, 0.77, 0.77, 1.15, 1.85, 2.81, 3.92, 5.06, 6.11, 6.95, 7.50, 7.69, 7.50, 6.95, 6.11],
            [1.05, 1.69, 2.57, 3.59, 4.64, 5.60, 6.37, 6.87, 7.04, 6.87, 6.37, 5.60, 4.64, 3.59, 2.57, 1.69, 1.05, 0.71, 0.71, 1.05, 1.69, 2.57, 3.59, 4.64, 5.60, 6.37, 6.87, 7.04, 6.87, 6.37, 5.60, 4.64, 3.59, 2.57, 1.69, 1.05, 0.71, 0.71, 1.05, 1.69, 2.57, 3.59, 4.64, 5.60, 6.37, 6.87, 7.04, 6.87, 6.37, 5.60],
            [0.99, 1.59, 2.42, 3.37, 4.35, 5.26, 5.98, 6.45, 6.61, 6.45, 5.98, 5.26, 4.35, 3.37, 2.42, 1.59, 0.99, 0.67, 0.67, 0.99, 1.59, 2.42, 3.37, 4.35, 5.26, 5.98, 6.45, 6.61, 6.45, 5.98, 5.26, 4.35, 3.37, 2.42, 1.59, 0.99, 0.67, 0.67, 0.99, 1.59, 2.42, 3.37, 4.35, 5.26, 5.98, 6.45, 6.61, 6.45, 5.98, 5.26],
            [0.95, 1.54, 2.34, 3.26, 4.21, 5.08, 5.79, 6.24, 6.40, 6.24, 5.79, 5.08, 4.21, 3.26, 2.34, 1.54, 0.95, 0.64, 0.64, 0.95, 1.54, 2.34, 3.26, 4.21, 5.08, 5.79, 6.24, 6.40, 6.24, 5.79, 5.08, 4.21, 3.26, 2.34, 1.54, 0.95, 0.64, 0.64, 0.95, 1.54, 2.34, 3.26, 4.21, 5.08, 5.79, 6.24, 6.40, 6.24, 5.79, 5.08]]
    else:
        print(f'doing {SettingsObject.TrainingData}.....')
        MyDatafile = open(SettingsObject.TrainingData)
        MyData = csv.reader(MyDatafile)
        for index, row in enumerate(MyData):
            if (index >= 590):
              

                print(len (row))
                print(len (row[-3:]))
            tempX = []
            for value in row:
                tempX.append(float(value))
            x.append(tempX)
            tempZ = []
            for target_index, TargetStock in enumerate(TargetStock_index_array):
                tempZ.append(float(tempX[TargetStock]))
            z.append(tempZ)

    DaysInData = len(x)
    SamplesPerday = len(x[0])
    #input_dim_z = len(z[0])
    output_dim = len(TargetStock_index_array)
    inputs = np.ndarray([DaysInData, 1, SamplesPerday], dtype=np.float32)
    #inputs = np.ndarray([len(x)-SettingsObject.trainingDataWindow+1, SettingsObject.trainingDataWindow, input_dim_x], dtype=np.float32)
    #input_last_day = np.ndarray([len(x)-SettingsObject.trainingDataWindow+1, input_dim_z], dtype=np.float32)
    labels =  np.ndarray([DaysInData, output_dim], dtype=np.float32)

    for ThisDay in range(DaysInData):
        try:
            for target_index, TargetStock in enumerate(TargetStock_index_array):

                try:
                    TargetDayIndex = int(ThisDay + SettingsObject.lookToTheFuture)
                    labels[ThisDay][target_index] = x[TargetDayIndex][TargetStock]
                except:
                    labels[ThisDay][target_index] = -100
          
            inputs[ThisDay][0] = x[ThisDay]
            
      
        except Exception as e:
            print('***************')
            print(e)
            print(i)
            print('***************')
            raise Exception ('Data preparation error ' + str(e))
        
    
    overwritetodisk(labels, SettingsObject.TrueAnswersfile)
    # Split data into train/test portions and combining all data from different files into a single array
    test_start = int(inputs.shape[0]-(inputs.shape[0]*SettingsObject.PredictionPart)) # simualating predicion
    if(test_start <= 0):
        raise Exception('Teststart <= 0')
    batch_size = 1

    train_inputs = inputs[:test_start]
    train_labels = labels[:test_start]
    #train_input_last_day = input_last_day[:test_start]

    eval_inputs = inputs
    eval_labels = labels
    #eval_input_last_day = input_last_day
 
 

    train_data = TensorDataset(torch.tensor(torch.from_numpy(train_inputs)), torch.tensor(torch.from_numpy(train_labels)))
    train_loader = DataLoader(train_data, shuffle=False, batch_size=1, drop_last=False)
    
    eval_data = TensorDataset(torch.tensor(eval_inputs), torch.tensor((eval_labels)))
    eval_loader = DataLoader(eval_data, shuffle=False, batch_size=1, drop_last=False)
    #for plotting
    
    return train_loader, eval_loader, output_dim, DaysInData, SamplesPerday, test_start, batch_size 

def get_device():
    if torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu") 
    return device

def get_target_stock_array(SettingsObject):
    TargetStock_index_array = []
    with open(SettingsObject.CompanysecbraFile) as MyCompany_sec_bra_File:
        MyCompany_sec_bra = json.load(MyCompany_sec_bra_File)

        my_targets = MyCompany_sec_bra[SettingsObject.currentsector][SettingsObject.currentbranch]
        
        with open(SettingsObject.StockindexFile) as MyStock_index_File:
            MyStock_index = json.load(MyStock_index_File)
            for company_namn in my_targets:
                try:
                    TargetStock_index_array.append(MyStock_index[company_namn])
                    SettingsObject.TargetStocknamearray.append([company_namn])
                    break
                except Exception as e:
                    print('not targeting ' + str(company_namn))
                    my_targets.remove(company_namn)
                    print(e)
        overwritetodisk(SettingsObject.TargetStocknamearray, SettingsObject.Targetsfile)
        return TargetStock_index_array

def clear_files_for_training(SettingsObject):
    if (os.path.exists(SettingsObject.TrainingAnswersfile)):
        if (os.path.exists(SettingsObject.TrainingAnswersfile + '_bak')):
            os.remove(SettingsObject.TrainingAnswersfile + '_bak')
        os.rename(SettingsObject.TrainingAnswersfile, SettingsObject.TrainingAnswersfile + '_bak')
        
    if (os.path.exists(SettingsObject.PredictionAnswersfile)):
        if (os.path.exists(SettingsObject.PredictionAnswersfile + '_bak')):
            os.remove(SettingsObject.PredictionAnswersfile + '_bak')
        os.rename(SettingsObject.PredictionAnswersfile, SettingsObject.PredictionAnswersfile + '_bak')
        
    if (os.path.exists(SettingsObject.TrueAnswersfile)):
        if (os.path.exists(SettingsObject.TrueAnswersfile + '_bak')):
            os.remove(SettingsObject.TrueAnswersfile + '_bak')
        os.rename(SettingsObject.TrueAnswersfile, SettingsObject.TrueAnswersfile + '_bak')
    if (os.path.exists(SettingsObject.Lossfile)):
        if (os.path.exists(SettingsObject.Lossfile + '_bak')):
            os.remove(SettingsObject.Lossfile + '_bak')
        os.rename(SettingsObject.Lossfile, SettingsObject.Lossfile + '_bak')

def mae(predictions, targets):
    differences = predictions - targets
    absolute_differences = np.absolute(differences)
    mean_absolute_differences = absolute_differences.mean()
    return mean_absolute_differences

def go():
    SettingsObject = Settings(False)
    
    device = get_device()
    #subprocess.Popen([r'plotter_start.bat'],  shell=True)
    Epoch_zero_time = datetime.now()
    time_to_change = Epoch_zero_time + timedelta(minutes=SettingsObject.stockTrainingTime)
    TargetStock_index_array = get_target_stock_array(SettingsObject)
    firsttime = True
    clear_files_for_training(SettingsObject)
    best_avg_loss = 10000000
    torch.cuda.empty_cache()  
    model_type="GRU"
    EPOCHS=500000
    useGRU = True
    train_loader, eval_loader, output_dim, DaysInData, DataPointsInday, test_start, batch_size = prepare_data(TargetStock_index_array)
    if(MockData):
        hidden_dim=20
    else:
        hidden_dim=int(DataPointsInday/10)
    n_layers = 2
    # Instantiating the models
    trainingdiff = []
    validationdiff = []
    if(not MockData):
        if (os.path.exists(SettingsObject.ModelPath + 'S' + SettingsObject.currentsector + 'B' + SettingsObject.currentbranch + 'D' + str(SettingsObject.lookToTheFuture) + 'W' + str(SettingsObject.trainingDataWindow) +'_model.pth')):
            if device.type == 'cuda':
                print('Loading model ' +SettingsObject.ModelPath + 'S' + SettingsObject.currentsector + 'B' + SettingsObject.currentbranch + 'D' + str(SettingsObject.lookToTheFuture) + 'W' + str(SettingsObject.trainingDataWindow) +'_model.pth to GPU')
                model = torch.load(SettingsObject.ModelPath + 'S' + SettingsObject.currentsector + 'B' + SettingsObject.currentbranch + 'D' + str(SettingsObject.lookToTheFuture) + 'W' + str(SettingsObject.trainingDataWindow) +'_model.pth', map_location=torch.device('cuda'))
            elif device.type == 'cpu':
                print('Loading model ' +SettingsObject.ModelPath + 'S' + SettingsObject.currentsector + 'B' + SettingsObject.currentbranch + 'D' + str(SettingsObject.lookToTheFuture) + 'W' + str(SettingsObject.trainingDataWindow) +'_model.pth to CPU')
                model = torch.load(SettingsObject.ModelPath + 'S' + SettingsObject.currentsector + 'B' + SettingsObject.currentbranch + 'D' + str(SettingsObject.lookToTheFuture) + 'W' + str(SettingsObject.trainingDataWindow) +'_model.pth', map_location=torch.device('cpu'))    
            else:
                raise Exception('No device..')
            with open(SettingsObject.trainingdifffile, newline='') as SettingsObject.trainingdifffile_read:
                accuracy_line = SettingsObject.trainingdifffile_read.readline()
                accuracy_line.replace("'", "")
                accuracy_splits = accuracy_line.split(',')
                for part in accuracy_splits:
                    trainingdiff.append(float(part))

        
            SettingsObject.trainingdifffile_read.close()

            with open(SettingsObject.validationdifffile, newline='') as SettingsObject.validationdifffile_read:
                accuracy_line = SettingsObject.validationdifffile_read.readline()
                accuracy_line.replace("'", "")
                accuracy_splits = accuracy_line.split(',')
                for part in accuracy_splits:
                    validationdiff.append(float(part))

        
            SettingsObject.validationdifffile_read.close()   
        else:
            if model_type=="GRU":
                print('Createing model GRU ' +SettingsObject.ModelPath + 'S' + SettingsObject.currentsector + 'B' + SettingsObject.currentbranch + 'D' + str(SettingsObject.lookToTheFuture) + 'W' + str(SettingsObject.trainingDataWindow) +'_model.pth to device ' + str(device))
                model = MyNet(useGRU , batch_size, hidden_dim, output_dim, n_layers)
    else:
        model = MyNet(useGRU , DataPointsInday, hidden_dim, output_dim, n_layers)
        
    model.lr = SettingsObject.lr  
    model.to(device)
    # Defining loss function and optimizer
    criterion = torch.nn.MSELoss()   # mean-squared error for regression
    optimizer = torch.optim.Adam(model.parameters(), lr=model.lr)
    for g in optimizer.param_groups:
        g['lr'] = model.lr    


    # Start training loop
    Grand_counter = 0
    torch.cuda.empty_cache()  
    while True:
        while(datetime.now() < time_to_change):
            print(f'Starting Training of {format(model_type)} model, device is {device} ')
            
            Grand_counter = Grand_counter + 1
            for epoch in range(1,EPOCHS+1):
                avg_loss = 0
                counter = 0
                trainoutputs = []
                temptrainingdiff = []
                tempvalidationdiff = []
                predictionsoutput = []
                train_loader_len = train_loader.dataset.tensors[0].shape[0]
                train_loader_modulus = int(train_loader_len/100)+1
                eval_loader_len = eval_loader.dataset.tensors[0].shape[0]
                eval_loader_modulus = int(eval_loader_len/100)+1
                #train
                model.train()
                print(f"Epoch train {str(epoch)}")
                h = model.init_hidden()
                h = h.data
                torch.autograd.set_detect_anomaly(True)
                for index, (input, label) in enumerate(train_loader):
                    
                    if(not MockData and index%train_loader_modulus == 0):
                        print(f"Epoch train {str(epoch)} {(index*100)/train_loader_len}% done..........", end='\r')                      
                    optimizer.zero_grad()
                    out, h = model(input.to(device).float(), h.to(device).float())
                    
                    diff = (label - out)

                    loss = criterion(out, label)

                    
                    loss.backward()
                            
                    optimizer.step()
                    
                    
                    temp_out = []
                    tempdiff = []
                    for items in out.view(-1):
                        temp_out.append(items.item())
                    
                    for item in diff.view(-1):
                        tempdiff.append(np.absolute(item.item()))
                    avrage_dif = sum(tempdiff)/len(tempdiff)
                    trainoutputs.append(temp_out)
                    temptrainingdiff.append(avrage_dif) 
                
                    h = h.detach()
                    
                with torch.no_grad():
                    h = model.init_hidden()
                    h = h.data
                    model.eval()
                    for index, (input, label) in enumerate(eval_loader):
                        if(not MockData and index%eval_loader_modulus == 0):
                            print(f"Epoch predict {str(epoch)} {(index*100)/eval_loader_len}% done..........", end='\r')                      
             
                        out, h = model(input.to(device).float(), h.to(device).float())
                    
                        temp_out = []
                        tempdiff = []
                        for items in out.view(-1):
                            temp_out.append(items.item())
                        
                        label = label.to(device)       
                        diff = (label - out)
                        for item in diff.view(-1):
                            tempdiff.append(np.absolute(item.item()))
                        avrage_dif = sum(tempdiff)/len(tempdiff)
                        
                        predictionsoutput.append(temp_out)
                        tempvalidationdiff.append(avrage_dif) 
                        h = h.detach()
                if firsttime:
                    best_avg_loss = 10000
                        
                trainingdiff.append(sum(temptrainingdiff)/len(temptrainingdiff))
                validationdiff.append(sum(tempvalidationdiff)/len(tempvalidationdiff))
                
                
                torch.cuda.empty_cache()  
                current_time = datetime.now()
                
                overwritelisttodisk(validationdiff, SettingsObject.Lossfile)
                overwritelisttodisk(trainingdiff, SettingsObject.trainingdifffile)
                overwritelisttodisk(validationdiff, SettingsObject.validationdifffile)
                if validationdiff[-1] < best_avg_loss:
                    best_avg_loss = validationdiff[-1]
                    filename = SettingsObject.ModelPath + 'S' + SettingsObject.currentsector + 'B' + SettingsObject.currentbranch + 'D' + str(SettingsObject.lookToTheFuture) + 'W' + str(SettingsObject.trainingDataWindow) +'_model.pth'
                    print(f"Saving {filename}..........")
                    torch.save(model, filename)  
                    
                
                
                
                print(validationdiff[-1])

                overwritetodisk(trainoutputs, SettingsObject.TrainingAnswersfile)
                overwritetodisk(predictionsoutput, SettingsObject.PredictionAnswersfile)
                firsttime = False
                time.sleep(1)

            del out
            torch.cuda.empty_cache() 
        currenttime = datetime.now()
        timetochange = currenttime + timedelta(minutes=SettingsObject.stockTrainingTime)
    
GDC = GetDataClass
# GDC.GetCompanyList()
# GDC.GetAllStockHistory()
# GDC.getworldkpi()
# GDC.WriteDataForTraining()
go()