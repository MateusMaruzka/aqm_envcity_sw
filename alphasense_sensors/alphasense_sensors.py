# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 16:39:50 2022

@author: maruzka
"""

import pickle as pi
import alphasense_sensors.dados_correcao_temp as dados_temp
import alphasense_sensors.dados_alphasense as dados_sens

import functools

def debug(func):
    """Print the function signature and return value"""
    @functools.wraps(func)
    def wrapper_debug(*args, **kwargs):
        args_repr = [repr(a) for a in args]                      # 1
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]  # 2
        signature = ", ".join(args_repr + kwargs_repr)           # 3
        print(f"Calling {func.__name__}({signature})")
        value = func(*args, **kwargs)
        print(f"{func.__name__!r} returned {value!r}")           # 4
        return value
    return wrapper_debug



class Alphasense_Sensors:
    
    fn_data = '/home/pi/envcity_sw_lora/alphasense_sensors/alphasense_sensor_data.pickle'

    def __init__(self, sensor_model, sensor_num):
        
        self.__sensor_num = sensor_num
        self.__sensor_model = sensor_model
       
        self.bt, self.gain, self.we_zero, self.ae_zero, \
        self.we_sensor, self.sensitivity, self.electronic_we,  \
        self.electronic_ae, self.no2_sensitivity = \
        self.__get_sensor_data(sensor_model, sensor_num)
        
        if self.__sensor_model == "NH3-B1":
            self.corrected_we = self.simple_conversion
            self.temp_correction_coef = None
        else:
            self.corrected_we, self.temp_correction_coef = self.__temperature_correction_func()
        
    def __temperature_correction_func(self):
        
        if self.__sensor_model == "SO2-B4":
           return self.__algorithm_4, dados_temp.ajuste_temp[self.__sensor_model]
        else:
            return self.__algorithm_1, dados_temp.ajuste_temp[self.__sensor_model]

    def __aux(self):
        
        if self.__sensor_model == "CO-B4" or self.__sensor_model == "H2S-B4":
            self.func_aux_wec = self.__algorithm_2
            # self.func_aux_wec.corr_temp = dados_temp.ajuste_temp[self.__sensor_model][1]

        else: 
            self.func_aux_wec = self.__algorithm_3
            # self.func_aux_wec.corr_temp = dados_temp.ajuste_temp[self.__sensor_model][2] 
    
    def get_sensorNumber(self):
        return self.__sensor_num
    
    def __get_sensor_data(self, sensor_model, sensor_num):
        
        with open(self.fn_data, "rb") as f:
            data = dados_sens.data[sensor_model][sensor_num]
            
        return data.values()
    
    def simple_conversion(self, raw_we, raw_ae):
        return (raw_we - self.electronic_we) - (raw_ae - self.electronic_ae)

    def no2_corr(self, no_ppm):
        return self.no2_sensitivity*no_ppm*self.gain

    def __algorithm_1(self, raw_we, raw_ae, temp):
        kt = self.temp_correction_coef[0][temp // 10 + 3]
        return (raw_we - self.electronic_we ) - kt*(raw_ae - self.electronic_ae)
    
    def __algorithm_2(self, raw_we, raw_ae, temp):
        kt = self.temp_correction_coef[1][temp // 10 + 3]
        return (raw_we - self.electronic_we) - \
        (self.we_zero / self.ae_zero)*kt*(raw_ae - self.electronic_ae)
    
    def __algorithm_3(self, raw_we, raw_ae, temp):
        kt = self.temp_correction_coef[2][temp // 10 + 3]
        return (raw_we - self.electronic_we) - (self.we_zero - self.ae_zero) \
               - kt*(raw_ae - self.electronic_ae)
               
    def __algorithm_4(self, raw_we, raw_ae, temp):
        kt = self.temp_correction_coef[3][temp // 10 + 3]
        return (raw_we - self.electronic_we) - self.we_zero - kt

    def PPB(self, raw_we, raw_ae, **kwargs):
        return self.corrected_we(raw_we = raw_we, raw_ae = raw_ae, **kwargs) / self.sensitivity

    @debug
    def all_algorithms(self, raw_we, raw_ae, temp):
        return (self.__algorithm_1(raw_we, raw_ae, temp), \
                self.__algorithm_2(raw_we, raw_ae, temp), \
                self.__algorithm_3(raw_we, raw_ae, temp), \
                self.__algorithm_4(raw_we, raw_ae, temp))
    
    def sensor_configuration(self):
        
        print("Model:", self.__sensor_model)
        print("Sensor Number:", self.__sensor_num)
        print("Board Type:", self.bt)
        print("Primary Algorithm:", self.corrected_we.__name__)
        # print("Secondary Algorithm:", self.func_aux_wec.__name__)
        print("Gain:", self.gain, "[mV/nA]")
        print("Sensitivity:", self.sensitivity, "[mV/ppb]")
        print("-----------Working Electrode-----------")
        print("Electronic WE:", self.electronic_we, "[mV]")
        print("WE Zero:", self.we_zero, "[mV]")
        print("WE sensor:", self.we_sensor, "[nA/ppm]")
        print("-----------Aux Electrode-----------")
        print("Electronic AE:", self.electronic_ae, "[mV]")
        print("AE Zero:", self.ae_zero, "[mV]")
        


def main():
    nh3 = Alphasense_Sensors("NH3-B1", "77240205")
    print(nh3.no2_sensitivity)
    
if __name__ == "__main__":
    main()
        
        
