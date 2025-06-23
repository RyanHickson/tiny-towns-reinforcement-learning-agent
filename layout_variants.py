import numpy as np

def rotate_90(layout):
    return np.rot90(layout)

def mirror(layout):
    return np.fliplr(layout)

def create_variants(layout):
    variants = []
    new_variant = layout.copy()
    for var in range(4):
        variants.append(new_variant)
        variants.append(mirror(new_variant))
        new_variant = rotate_90(new_variant)
    return variants