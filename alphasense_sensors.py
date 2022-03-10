# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 16:39:50 2022

@author: maruzka
"""

import pickle as pi


class Alphasense_Sensors:
    
    fn_data = 'alphasense_sensor_data.pickle'

    def __init__(self, sensor_model, sensor_num):
        
        self.__sensor_num = sensor_num
        self.__sensor_model = sensor_model
        
        self.bt, self.gain, self.we_zero, self.ae_zero, \
        self.we_sensor, self.sensitivity, self.electronic_we,  \
        self.electronic_ae, self.no2_sensitivity = \
        self.__get_sensor_data(sensor_model, sensor_num)
        

        if sensor_model == "SO2-B4":
            self.func_wec = self.__algorithm_4
        else:
            self.func_wec = self.__algorithm_1
        
        if sensor_model == "CO-B4" or sensor_model == "H2S-B4":
            self.func_aux_wec = self.__algorithm_2
        else: 
            self.func_aux_wec = self.__algorithm_3
        
        
    def get_sensorType(self):
        return self.__sensor_type
    
    def get_sensorNumber(self):
        return self.__sensor_number
    
    def __get_sensor_data(self, sensor_model, sensor_num):
        
        with open(self.fn_data, "rb") as f:
            data = pi.load(f)
            data = data[sensor_model][sensor_num]
            
        return data.values()
            
    def __algorithm_1(self, raw_we, raw_ae):
        kt = 1 # TODO
        return (raw_we - self.electronic_we) - kt*(raw_ae - self.electronic_ae)
    
    def __algorithm_2(self, raw_we, raw_ae):
        kt = 1 # TODO
        return (raw_we - self.electronic_we) - \
        (self.we_zero / self.ae_zero)*kt*(raw_ae - self.electronic_ae)
    
    def __algorithm_3(self, raw_we, raw_ae):
        kt = 1 # TODO
        return (raw_we - self.electronic_we) - (self.we_zero - self.ae_zero) \
               - kt*(raw_ae - self.electronic_ae)
               
    def __algorithm_4(self, raw_we, raw_ae):
        kt = 1 # TODO
        return (raw_we - self.electronic_we) - self.we_zero - kt
    
    
    def PPM(self, raw_we, raw_ae, algorithm = "suggested"):
        if algorithm == "suggested":
            return func_wec(raw_we = raw_we, raw_ae = raw_ae) / self.sensitivity
        else:
            return func_aux_wec(raw_we = raw_we, raw_ae = raw_ae) / self.sensitivity

          
    
        
        
def main():
    
    fn_alpha_s = 'alphasense_sensor_data.pickle'
    
    co_b4 = Alphasense_Sensors("CO-B4", "162741358") 
    
    print(co_b4.gain)
  
    
    

if __name__ == "__main__":
    main()
        
        