import numpy as np

def rotate90(layout):
    return np.rot90(layout)

def mirror(layout):
    return np.fliplr(layout)

def createVariants(layout):
    variants = []
    newVariant = layout.copy()
    for var in range(4):
        variants.append(newVariant)
        variants.append(mirror(newVariant))
        newVariant = rotate90(newVariant)
    return variants