"""
python routines for window function generation
"""
import healpy as hp, pylab as plt, numpy as np, astropy.io.fits as pyfits
from pixell import enmap,curvedsky
from pspy import sph_tools
import scipy
import os, sys


def get_distance(binary):
    
    """Get the distance to the closest masked pixels for CAR and healpix so_map binary.
        
    Parameters
    ----------
    binary: so_map
      a so_map with binary data (1 is observed, 0 is masked)
    """
    
    dist=binary.copy()
    if binary.pixel=='HEALPIX':
        dist.data= enmap.distance_transform_healpix(binary.data, method="heap")
        dist.data*=180/np.pi
    if binary.pixel=='CAR':
        pixSize_arcmin= np.sqrt(binary.data.pixsize()*(60*180/np.pi)**2)
        dist.data[:]= scipy.ndimage.distance_transform_edt(binary.data)
        dist.data[:]*=pixSize_arcmin/60
    return dist


def create_apodization(binary, apo_type, apo_radius_degree):
    
    """Create a apodized window function from a binary mask.
    
    Parameters
    ----------
    binary: so_map
      a so_map with binary data (1 is observed, 0 is masked)
    apo_type: string
      the type of apodisation you want to use ("C1","C2" or "Rectangle")
    apo_radius: float
      the apodisation radius in degrees
    """

    if apo_type=='C1':
        window=apod_C1(binary,apo_radius_degree)
    if apo_type=='C2':
        window=apod_C2(binary,apo_radius_degree)
    if apo_type=='Rectangle':
        if binary.pixel=='HEALPIX':
            print( 'no rectangle apod for healpix map')
            sys.exit()
        if binary.pixel=='CAR':
            window= apod_rectangle(binary,apo_radius_degree)

    return window

def apod_C2(binary,radius):
    
    """Create a C2 apodisation as defined in https://arxiv.org/pdf/0903.2350.pdf
        
    Parameters
    ----------
    binary: so_map
        a so_map with binary data (1 is observed, 0 is masked)
    apo_radius: float
        the apodisation radius in degrees

    """
    
    if radius==0:
        return binary
    else:
        dist=get_distance(binary)
        win=binary.copy()
        id=np.where(dist.data> radius)
        win.data=dist.data/radius-np.sin(2*np.pi*dist.data/radius)/(2*np.pi)
        win.data[id]=1
        
    return(win)

def apod_C1(binary,radius):
    
    """Create a C1 apodisation as defined in https://arxiv.org/pdf/0903.2350.pdf
        
    Parameters
    ----------
    binary: so_map
      a so_map with binary data (1 is observed, 0 is masked)
    apo_radius: float
      the apodisation radius in degrees
        
    """
    
    if radius==0:
        return binary
    else:
        dist=get_distance(binary)
        win=binary.copy()
        id=np.where(dist.data> radius)
        win.data=1./2-1./2*np.cos(-np.pi*dist.data/radius)
        win.data[id]=1
    
    return(win)

def apod_rectangle(binary,radius):
    
    """Create an apodisation able for rectangle window (in CAR) (smoother at the corner)
        
    Parameters
    ----------
    binary: so_map
      a so_map with binary data (1 is observed, 0 is masked)
    apo_radius: float
      the apodisation radius in degrees
        
    """
    
    #TODO: clean this one
    
    if radius==0:
        return binary
    else:
        shape= binary.data.shape
        wcs= binary.data.wcs
        Ny,Nx=shape
        pixScaleY,pixScaleX= enmap.pixshape(shape, wcs)
        win=binary.copy()
        win.data= win.data*0+1
        winX=win.copy()
        winY=win.copy()
        Id=np.ones((Ny,Nx))
        degToPix_x=np.pi/180/pixScaleX
        degToPix_y=np.pi/180/pixScaleY
        lenApod_x=int(radius*degToPix_x)
        lenApod_y=int(radius*degToPix_y)
    
        for i in range(lenApod_x):
            r=float(i)
            winX.data[:,i]=1./2*(Id[:,i]-np.cos(-np.pi*r/lenApod_x))
            winX.data[:,Nx-i-1]=winX.data[:,i]
        for j in range(lenApod_y):
            r=float(j)
            winY.data[j,:]=1./2*(Id[j,:]-np.cos(-np.pi*r/lenApod_y))
            winY.data[Ny-j-1,:]=winY.data[j,:]

        win.data=winX.data*winY.data
        return(win)

def get_spinned_windows(w,lmax,niter):
    
    """Compute the spin window functions (for pure B modes method)
        
    Parameters
    ----------
    w: so_map
      map of the window function
    lmax: integer
      maximum value of the multipole for the harmonic transform
    niter: integer
      number of iteration for the harmonic transform
      
    """

    
    template=np.array([w.data.copy(),w.data.copy()])
    s1_a,s1_b,s2_a,s2_b=w.copy(),w.copy(),w.copy(),w.copy()
    
    if w.pixel=='CAR':
        template=enmap.samewcs(template,w.data)
    
    wlm = sph_tools.map2alm(w,lmax=lmax,niter=niter)
    ell = np.arange(lmax)
    filter_1=-np.sqrt((ell+1)*ell)
    filter_2=-np.sqrt((ell+2)*(ell+1)*ell*(ell-1))

    filter_1[:1]=0
    filter_2[:2]=0
    wlm1_e= hp.almxfl(wlm,filter_1)
    wlm2_e= hp.almxfl(wlm,filter_2)
    wlm1_b = np.zeros_like(wlm1_e)
    wlm2_b = np.zeros_like(wlm2_e)

    w1=template.copy()
    w2=template.copy()
    
    if w.pixel=='HEALPIX':
        curvedsky.alm2map_healpix( np.array([wlm1_e,wlm1_b]), w1, spin=1)
        curvedsky.alm2map_healpix( np.array([wlm2_e,wlm2_b]), w2, spin=2)
    if w.pixel=='CAR':
        curvedsky.alm2map(np.array([wlm1_e,wlm1_b]), w1, spin=1)
        curvedsky.alm2map(np.array([wlm2_e,wlm2_b]), w2, spin=2)
    
    s1_a.data[w.data != 0]=w1[0][w.data != 0]
    s1_b.data[w.data != 0]=w1[1][w.data != 0]
    s2_a.data[w.data != 0]=w2[0][w.data != 0]
    s2_b.data[w.data != 0]=w2[1][w.data != 0]
    
    return s1_a,s1_b,s2_a,s2_b


