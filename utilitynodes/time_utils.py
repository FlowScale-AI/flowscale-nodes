import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Delay:
  """
  Simulate network delay
  """
  
  @classmethod
  def INPUT_TYPES(cls):
    return {
      "required": {
        "delay": ("INT",)
      },
      "optional": {
        "trigger": ("*",)
      }
    }
    
  @classmethod
  def VALIDATE_INPUTS(s, input_types):
    return True
  
  RETURN_TYPES = ("*", )
  RETURN_NAMES = ("delayed_response", )
  FUNCTION = "delay"
  CATEGORY = "FlowScale/Utils/Time"
  
  def delay(self, delay: int):
    time.sleep(delay)
    return "Delayed by {} seconds".format(delay)
