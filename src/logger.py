import logging
from datetime import datetime
import os

log_file_formate=f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
log_file_path=os.path.join(os.getcwd(),"logs")

os.makedirs(log_file_path,exist_ok=True)
LOG_FILE=os.path.join(log_file_path,log_file_formate)

logging.basicConfig(
    level=logging.INFO,
    filename=LOG_FILE,
    format='[%(asctime)s] %(lineno)d %(levelname)s - %(message)s',
)


if __name__=='__main__':
    logging.info("Logging has started...")