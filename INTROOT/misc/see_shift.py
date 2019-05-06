import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def gauss_function(x, a, x0, sigma, dc):
    """
    A standard 1D gaussian function (for fitting against)]=

    :param x: numpy array (1D), the x data points
    :param a: float, the amplitude
    :param x0: float, the mean of the gaussian
    :param sigma: float, the standard deviation (FWHM) of the gaussian
    :param dc: float, the constant level below the gaussian

    :return gauss: numpy array (1D), size = len(x), the output gaussian
    """
    return a * np.exp(-0.5 * ((x - x0) / sigma) ** 2) + dc

def update_data(num, image, dataarr):
    image.set_data(dataarr[num])
    return [image]


size = 10
length = 7
shifts = [1/2000.0, None, 1/200.0, None, 1/20.0, None, 1/2.0]
shiftlabels = ['1/2000', '', '1/200', '', '1/20', '', '1/2']

ynochange = np.zeros((length, size))
ychange = np.zeros((length, size))

x = np.arange(size)
x = x - size // 2


for it, shift in enumerate(shifts):

    if shift is None:
        continue

    xmed = x[size // 2]

    xshift = x + shift
    xmedshift = xshift[size // 2]

    yshift = gauss_function(xshift, 1.0, xmedshift, 1.0, 0.0)
    y0 = gauss_function(x, 1.0, xmed, 1.0, 0.0)


    ynochange[it] = y0
    ychange[it] = np.interp(x, xshift, yshift)




# plot
fig = plt.figure()
frame = plt.subplot(111)

im = frame.imshow(ynochange)
allimages = [ynochange, ychange]

frame.set_yticks(np.arange(len(shifts)))
frame.set_yticklabels(shiftlabels)

line_ani = animation.FuncAnimation(fig, update_data, len(allimages),
                                   fargs=(im, allimages),
                                   interval=500, blit=True)

plt.show()
plt.close()