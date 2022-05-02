from __future__ import division
from __future__ import print_function

import numpy as np
from skimage.measure import label
from skimage.morphology import remove_small_objects
from skimage.segmentation import watershed
from skimage.transform import resize


def binary_connected(
    volume, thres=0.5, thres_small=3, scale_factors=(1.0, 1.0, 1.0)
):
    r"""Convert binary foreground probability maps to instance masks via
    connected-component labeling.

    Args:
        volume (numpy.ndarray): foreground probability of shape :math:`(C, Z, Y, X)`.
        thres (float): threshold of foreground. Default: 0.8
        thres_small (int): size threshold of small objects to remove. Default: 128
        scale_factors (tuple): scale factors for resizing in :math:`(Z, Y, X)` order. Default: (1.0, 1.0, 1.0)
    """
    semantic = volume[0]
    foreground = semantic > thres  # int(255 * thres)
    segm = label(foreground)
    segm = remove_small_objects(segm, thres_small)

    if not all(x == 1.0 for x in scale_factors):
        target_size = (
            int(semantic.shape[0] * scale_factors[0]),
            int(semantic.shape[1] * scale_factors[1]),
            int(semantic.shape[2] * scale_factors[2]),
        )
        segm = resize(
            segm,
            target_size,
            order=0,
            anti_aliasing=False,
            preserve_range=True,
        )

    return segm


def binary_watershed(
    volume,
    thres_seeding=0.9,
    thres_small=10,
    thres_objects=0.3,
    scale_factors=(1.0, 1.0, 1.0),
    rem_seed_thres=3,
):
    r"""Convert binary foreground probability maps to instance masks via
    watershed segmentation algorithm.

    Note:
        This function uses the `skimage.segmentation.watershed <https://github.com/scikit-image/scikit-image/blob/master/skimage/segmentation/_watershed.py#L89>`_
        function that converts the input image into ``np.float64`` data type for processing. Therefore please make sure enough memory is allocated when handling large arrays.

    Args:
        volume (numpy.ndarray): foreground probability of shape :math:`(C, Z, Y, X)`.
        thres_seeding (float): threshold for seeding. Default: 0.98
        thres_objects (float): threshold for foreground objects. Default: 0.3
        thres_small (int): size threshold of small objects removal. Default: 10
        scale_factors (tuple): scale factors for resizing in :math:`(Z, Y, X)` order. Default: (1.0, 1.0, 1.0)
        rem_seed_thres: threshold for small seeds removal. Default : 3
    """
    semantic = volume[0]
    seed_map = semantic > thres_seeding
    foreground = semantic > thres_objects
    seed = label(seed_map)
    seed = remove_small_objects(seed, rem_seed_thres)
    segm = watershed(-semantic.astype(np.float64), seed, mask=foreground)
    segm = remove_small_objects(segm, thres_small)

    if not all(x == 1.0 for x in scale_factors):
        target_size = (
            int(semantic.shape[0] * scale_factors[0]),
            int(semantic.shape[1] * scale_factors[1]),
            int(semantic.shape[2] * scale_factors[2]),
        )
        segm = resize(
            segm,
            target_size,
            order=0,
            anti_aliasing=False,
            preserve_range=True,
        )

    return np.array(segm)