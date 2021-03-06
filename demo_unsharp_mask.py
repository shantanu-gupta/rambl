""" assume 32-bit floats being used everywhere """
import numpy as np

def generate_bitloss_mask(shape, approx_bits, loss_prob, num_refreshes):
    loss_prob = 1 - ((1 - loss_prob) ** max(1, num_refreshes))
    mask = np.zeros(shape, dtype=np.int32)
    for b in approx_bits:
        l = np.random.random(shape) < loss_prob
        mask = mask | np.left_shift(l.astype(np.int32), b)
    return mask

def apply_bitloss_mask(A, mask):
    # We only let the LSBs of the mantissa get lost, so this is enough
    return (A.view(np.int32) & np.invert(mask)).view(np.float32)

def main():
    from skimage.data import moon
    from skimage.util import img_as_float32
    from skimage.filters import unsharp_mask
    import matplotlib.pyplot as plt

    A = img_as_float32(moon())
    Af0 = unsharp_mask(A, radius=5, amount=2)

    NUM_APPROX_BITS = 20
    Ac = apply_bitloss_mask(A, generate_bitloss_mask(A.shape,
                                                    range(NUM_APPROX_BITS),
                                                    1e-1,
                                                    10))
    Afc = unsharp_mask(Ac, radius=5, amount=2)

    plt.figure()
    plt.imshow(np.vstack((np.hstack((A, Af0)),
                          np.hstack((Ac, Afc)))), cmap='gray')
    plt.title('\n'.join(
                ('top-left: original input', 
                 'top-right: original filter output',
                 'bottom-left: approx input ({}/23 bad mantissa bits)'
                    .format(NUM_APPROX_BITS), 
                 'bottom-right: approx output')))
    plt.show()
    return

if __name__ == "__main__":
    main()

