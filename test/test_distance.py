import numpy as np
import healpy as hp
import pylab as plt
import time
from pixell import enmap
from pspy import so_window,so_map


nside=1024

binary=np.zeros(12*nside**2)

maxang = 20.

veccenter = hp.ang2vec(np.pi/2, 0)
vecpix = hp.pix2vec(nside, np.arange(12*nside**2))
cosang = np.dot(veccenter, vecpix)
maskok = np.degrees(np.arccos(cosang)) < maxang
binary[maskok]=1


binary_temp=so_map.healpix_template(1,nside,coordinate=None)
binary_temp.data=binary

binary_temp.plot()
dist= so_window.get_distance(binary_temp)

dist.plot()
