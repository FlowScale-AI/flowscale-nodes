import asyncio
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FSDelay:
    """
    Simulate network delay while passing through the input data
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "delay": ("INT", {"default": 1, "min": 0, "max": 60, "step": 1}),
                "use_async": ("BOOLEAN", {"default": True}),
            },
            "optional": {"trigger": ("*",)},
        }

    @classmethod
    def VALIDATE_INPUTS(cls, input_types):
        return True

    RETURN_TYPES = ("*",)
    RETURN_NAMES = ("delayed_response",)
    EXPERIMENTAL = True
    FUNCTION = "delay"
    CATEGORY = "FlowScale/Utils/Time"

    def delay(self, delay: int, use_async: bool = True, trigger=None):
        logger.info(f"Delaying for {delay} seconds (async: {use_async})...")

        if use_async and delay > 0:
            # Use async delay to not block other operations
            try:
                asyncio.run(asyncio.sleep(delay))
            except RuntimeError:
                # Fallback to sync if no event loop
                time.sleep(delay)
        else:
            time.sleep(delay)

        # Return the trigger input as-is after the delay
        return (trigger,) if trigger is not None else None
