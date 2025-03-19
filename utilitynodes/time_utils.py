import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Delay:
    """
    Simulate network delay while passing through the input data
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "delay": ("INT", {"default": 1, "min": 0, "max": 60, "step": 1})
            },
            "optional": {
                "trigger": ("*",)
            }
        }
        
    @classmethod
    def VALIDATE_INPUTS(s, input_types):
        return True
    
    RETURN_TYPES = ("*",)
    RETURN_NAMES = ("delayed_response",)
    FUNCTION = "delay"
    CATEGORY = "FlowScale/Utils/Time"
    
    def delay(self, delay: int, trigger=None):
        logger.info(f"Delaying for {delay} seconds...")
        time.sleep(delay)
        # Return the trigger input as-is after the delay
        return (trigger,)
