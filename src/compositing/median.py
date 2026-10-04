import numpy as np


class MedianComposite:
    """
    Computes the annual median composite from a stacked
    collection of processed Landsat scenes.

    Uses memory-efficient float32 processing.
    """


    def create(
        self,
        stack,
    ) -> np.ndarray:


        # ---------------------------------------------------------
        # Convert list of images into numpy stack
        # ---------------------------------------------------------

        if isinstance(stack, list):

            if len(stack) == 0:

                raise ValueError(
                    "Cannot create a composite from an empty image stack."
                )


            stack = np.stack(
                stack,
                axis=0,
            )



        # ---------------------------------------------------------
        # Validate stack
        # ---------------------------------------------------------

        if stack.size == 0:

            raise ValueError(
                "Cannot create a composite from an empty image stack."
            )



        # ---------------------------------------------------------
        # Reduce memory usage
        # ---------------------------------------------------------

        stack = stack.astype(
            np.float32,
            copy=False,
        )



        # ---------------------------------------------------------
        # Remove scenes that contain no valid pixels
        # ---------------------------------------------------------

        valid_scenes = ~np.all(
            np.isnan(stack),
            axis=(1, 2),
        )


        if np.any(valid_scenes):

            stack = stack[
                valid_scenes
            ]



        if stack.shape[0] == 0:

            raise ValueError(
                "All scenes contain only NaN values."
            )



        # ---------------------------------------------------------
        # Calculate median composite
        # ---------------------------------------------------------

        composite = np.nanmedian(
            stack,
            axis=0,
        )



        return composite.astype(
            np.float32
        )