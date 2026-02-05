import sys
from src.logger import logging

def error_message_detail(error,error_details:sys):
    _,_,exe_tb=error_details.exc_info()
    filename=exe_tb.tb_frame.f_code.co_filename
    error_message=f"Error Occurred in {filename} in the line number {exe_tb.tb_lineno} and error message is {error}"

    return error_message

class CustomException(Exception):
    def __init__(self,error_message,error_details:sys):
        super().__init__(error_message)
        self.error_message=error_message_detail(error_message,error_details=error_details)



if __name__=='__main__':
    try:
        a=1/0
    except Exception as e:
        logging.info(CustomException(e,sys).error_message)
        raise CustomException(e,sys)
        
    
