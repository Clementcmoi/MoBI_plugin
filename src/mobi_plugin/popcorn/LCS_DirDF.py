# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 15 13:46:27 2021.

@author: quenot
"""
import numpy as np
from scipy.ndimage.filters import median_filter
from matplotlib.colors import hsv_to_rgb
from numba import jit
from . import frankoChellappa as fc
from .fourier_integration import fourier_solver

from scipy import signal


def myGradient(img):
    coins=0.3
    # kernely = np.array([[coins,1,coins],[0,0,0],[-coins,-1,-coins]])
    # kernelx = np.array([[coins,0,-coins],[1,0,-1],[coins,0,-coins]])
    kernely = np.array([[1],[0],[-1]])
    kernelx = np.array([[1,0,-1]])
    edges_x = signal.convolve2d(img,kernelx,boundary='wrap', mode='same')
    edges_y = signal.convolve2d(img,kernely,boundary='wrap', mode='same')
    return edges_x, edges_y
    

def LCS_DDF(experiment):
    """Calculates the displacement images from sample and reference images using the LCS system
    

    Args:
        experiment (PhaseRetrievalClass): class with all parameters as attributes.

    Returns:
        Dx (NUMPY ARRAY): the displacements along x axis.
        Dy (NUMPY ARRAY): the displacements along y axis.
        absoprtion (NUMPY ARRAY): the absorption.

    """
    nbOfVariables=6
    if nbOfVariables>experiment.nb_of_point:
        raise Exception("Not enough point to solve LCS dir DF (min 6) only %d given" %experiment.nb_of_point)
    
    
    Nz, Nx, Ny=experiment.reference_images.shape
    LHS=np.ones(((experiment.nb_of_point, Nx, Ny)))
    RHS=np.ones((((experiment.nb_of_point,nbOfVariables, Nx, Ny))))
    solution=np.ones(((nbOfVariables, Nx, Ny)))

    #Prepare system matrices
    for i in range(experiment.nb_of_point):

        #Right handSide
        # gX_IrIr,gY_IrIr=np.gradient(experiment.reference_images[i])
        # lapIr=laplace(experiment.reference_images[i])
        
        gX_IrIr,gY_IrIr=myGradient(experiment.reference_images[i] )
        gXX_IrIr,gYX_IrIr=myGradient(gX_IrIr)
        gXY_IrIr,gYY_IrIr=myGradient(gY_IrIr)
        
        
        
        RHS[i]=[experiment.sample_images[i],gX_IrIr, gY_IrIr, -gXX_IrIr, -gYY_IrIr, -gXY_IrIr]
        LHS[i]=experiment.reference_images[i]

    #Solving system for each pixel 
    for i in range(Nx):

        for j in range(Ny):
            a=RHS[:,:,i,j]
            b=LHS[:,i,j]
            Q,R = np.linalg.qr(a) # qr decomposition of A
            Qb = np.dot(Q.T,b) # computing Q^T*b (project b onto the range of A)
            
            if R[2,2]==0 or R[1,1]==0 or R[0,0]==0 or R[3,3]==0 or R[4,4]==0 or R[5,5]==0:
                temp=[1,0,0,0,0,0]
            else:
                temp = np.linalg.solve(R,Qb) # solving R*x = Q^T*b
            solution[:,i,j]=temp
        
    absoprtion=1/solution[0]
    Dx=solution[1]
    Dy=solution[2]
    Deff_yy=solution[3]
    Deff_xx=solution[4]
    Deff_xy=solution[5]
    
    #Bit of post-processing
    #Limiting displacement to a threshold
    displacementLimit=experiment.max_shift
    Dx[Dx<-displacementLimit]=-displacementLimit
    Dx[Dx>displacementLimit]=displacementLimit
    Dy[Dy<-displacementLimit]=-displacementLimit
    Dy[Dy>displacementLimit]=displacementLimit
    #Trying different filters
        
    return Dx, Dy, absoprtion, Deff_xx, Deff_yy, Deff_xy



def normalize(Image):
    Imageb=(Image-np.min(Image))/(np.max(Image)-np.min(Image))
    return Imageb


@jit(nopython=True)
def fast_loop_theta(thetapad, saturation, gaussian, Nx, Ny, size):
    thetaresult=np.zeros((Nx,Ny))
    i0=0
    j0=0
    for i in range(size, Nx+size):
        for j in range(size, Ny+size):
            patch=thetapad[i-size:i+size,j-size:j+size]*2
            mask=np.zeros((size*2, size*2))
            # mask[patch!=0]=1
            for k in range(size*2):
                for l in range(size*2):
                    if patch[k,l]!=0:
                        mask[k,l]=1
            cg=gaussian*np.cos(patch)  #filtrage de l'orientation sur une zone
            wcos=np.sum(gaussian*np.cos(patch)*mask)
            wsin=np.sum(gaussian*np.sin(patch)*mask)
            norm=np.sqrt(wcos**2+wsin**2)
            saturation[i0,j0]=norm
            # wcos=np.median(np.cos(patch))
            # wsin=np.median(np.sin(patch))            
            if wcos==0 and wsin==0:
                newVal=0
            else:
                newVal=np.arctan2(wsin,wcos)
                # print(newVal)
            thetaresult[i0,j0]=newVal/2          
            j0+=1
        i0+=1
        j0=0
    return thetaresult, saturation
    
def create_gaussian_shape(sigma):
    size=round(sigma*3)
    Qx, Qy = np.meshgrid((np.arange(0, 2*size) - np.floor(size) - 1), (np.arange(0, 2*size) - np.floor(size) - 1)) #frequency ranges of the images in fqcy space

    g = np.exp(-(((Qx)**2) / 2. / sigma**2 + ((Qy)**2) / 2. / sigma**2))
    return g/np.sum(g)
    
def correctTheta(theta, sigma=5):
    if sigma==0:
        sigma=5 #valeur ecart type gaussienne
    size=round(sigma*3)
    gaussian=create_gaussian_shape(sigma)
    Nx, Ny=theta.shape
    saturation=np.zeros((Nx,Ny))
    thetapad=np.pad(theta, size, mode='reflect')
    
    thetaresult, saturation=fast_loop_theta(thetapad,saturation, gaussian, Nx, Ny, size)
    thetaresult[thetaresult<0]+=np.pi
    saturation=saturation/np.max(saturation)
    
    return  thetaresult,saturation


def std_normalize(image, n_std=3, no_min=False):
    std_dev=np.std(image)
    mean_image=np.mean(image)
    if no_min==True:
        min_im=0
    else:
        min_im=mean_image-n_std*std_dev
    max_im=mean_image+n_std*std_dev
    image=(image-min_im)/(max_im-min_im)
    image=np.clip(image, 0, 1)
    return image

def processProjectionLCS_DDF(experiment):
    """
    This function calls PavlovDirDF to compute the tensors of the directional dark field and the thickness of the sample
    The function should also convert the tensor into a coloured image
    """
    Nx, Ny= experiment.sample_images[0].shape
    
    #Calculate directional darl field
    dx, dy, absorption, Deff_xx, Deff_yy, Deff_xy = LCS_DDF(experiment)
    
    if experiment.LCS_median_filter !=0:
        dx=median_filter(dx,size=experiment.LCS_median_filter)
        dy=median_filter(dy,size=experiment.LCS_median_filter)

    # Compute the phase gradient from displacements (linear relationship)
    # magnification=(experiment['distSO']+experiment['distOD'])/experiment['distSO'] #Not sure I need to use this yet
   
    
   
    dphix=dx*(experiment.pixel/experiment.dist_object_detector)*experiment.getk()
    dphiy=dy*(experiment.pixel/experiment.dist_object_detector)*experiment.getk()
    
    padForIntegration=False
    padSize=1000
    if padForIntegration:
        dphix = np.pad(dphix, ((padSize, padSize), (padSize, padSize)),mode='reflect')  # voir is edge mieux que reflect
        dphiy = np.pad(dphiy, ((padSize, padSize), (padSize, padSize)),mode='reflect')  # voir is edge mieux que reflect
    
    # Compute the phase from phase gradients with 3 different methods (still trying to choose the best one)
    # The sampling step for the gradient is the magnified pixel size
    magnificationFactor = (experiment.dist_object_detector + experiment.dist_source_object) / experiment.dist_source_object
    gradientSampling = experiment.pixel / magnificationFactor
    phiFC = fc.frankotchellappa(dphix, dphiy, 'antisym')*gradientSampling
    phiK = fourier_solver(dphix, dphiy, gradientSampling, gradientSampling, solver='kottler')
    #phiLS = ls_integration.least_squares(dphix, dphiy, gradientSampling, gradientSampling, model='southwell')
    
    if (padForIntegration and padSize > 0):
        phiFC = phiFC[padSize:padSize + Nx, padSize:padSize + Ny]
        phiK = phiK[padSize:padSize + Nx , padSize:padSize + Ny]
        #phiLS = phiLS[padSize:padSize + Nx, padSize:padSize + Ny]
        

        
    
    a11=(Deff_xy*Deff_yy)
    a22=(Deff_xy*Deff_xx)
    a12=Deff_xx*Deff_yy/2
        
    A=a11
    C=a22
    B=a12
    maskEllipsce=1-((A>0)*(A*C-B**2>0))
    
    theta=0.5*np.arctan2(2*a12,a11-a22)
    
    Ap1=np.abs(a11*np.sin(theta)**2+a22*np.cos(theta)**2+2*a12*np.sin(theta)*np.cos(theta))
    Bp1=np.abs(a11*np.cos(theta)**2+a22*np.sin(theta)**2-2*a12*np.sin(theta)*np.cos(theta))
    Ap=np.max([Ap1,Bp1], axis=0)
    Bp=np.min([Ap1,Bp1], axis=0)
    a=np.sqrt(Ap)
    b=np.sqrt(Bp)
    theta[Ap1<Bp1]+=np.pi/2
    theta[theta<0]+=np.pi
    
    # excentricity=np.sqrt(1-b/a)
    excentricity=abs(a-b)#(np.sqrt(a**2+b**2)/(a)-1)*2
    
    excentricity[maskEllipsce]=0
    area=(a*b)
    area[area<0]=0
    excentricity[excentricity>1]=1
    
    #Post processing tests
    alpha=0.0000001
    Deff_xx=abs(Deff_xx)
    Deff_yy=abs(Deff_yy)
    sign_Deff_xy=np.sign(Deff_xy)*1.

        
    threshold=1 #RANDOMLY CHOSEN CLIP VALUE
    Deff_yy[abs(Deff_yy)>threshold]=alpha
    Deff_xx[abs(Deff_xx)>threshold]=alpha
    Deff_xy[abs(Deff_xy)>threshold]=alpha*sign_Deff_xy[abs(Deff_xy)>threshold]
    Deff_yy[abs(Deff_yy)==0]=alpha
    Deff_xx[abs(Deff_xx)==0]=alpha
    Deff_xy[abs(Deff_xy)==0]=alpha*sign_Deff_xy[abs(Deff_xy)==0]
    
    #Median filter
    medFiltSize=experiment.LCS_median_filter
    if medFiltSize!=0:
        #thickness=median_filter(thickness, medFiltSize)
        Deff_xx=median_filter(Deff_xx, medFiltSize)
        Deff_yy=median_filter(Deff_yy, medFiltSize)
        Deff_xy=median_filter(Deff_xy, medFiltSize)
    if medFiltSize!=0:
        area=median_filter(area, medFiltSize)
        excentricity=median_filter(excentricity, medFiltSize)
    stdarea=np.std(area)
    area=abs(area)*1e3#/(3*stdarea)
    area[area>1]=1
    
    #NORMALIZATION
    # Deff_xx[Deff_xx>1]=1
    # Deff_yy[Deff_yy>1]=1
    # # Deff_xy=abs(Deff_xy)
    # Deff_xy[Deff_xy>1]=1
    
    IntensityDeff=np.sqrt((Deff_xx**2+Deff_yy**2+Deff_xy**2)/3)
    
    theta, sat=correctTheta(theta, medFiltSize*2) #theta=carte des orientations sur l'image, medFiltSize=ecart type gaussienne
    theta=theta/np.pi
    
    #Trying to create a coloured image from tensor (method probably wrong for now)
    colouredImage=np.zeros(((Nx, Ny,3)))
    colouredImage[:,:,0]=Deff_xx
    colouredImage[:,:,1]=Deff_yy
    colouredImage[:,:,2]=abs(Deff_xy)
    
    colouredImageExc=np.zeros(((Nx, Ny,3)))
    colouredImageExc[:,:,0]=theta
    colouredImageExc[:,:,1]=sat
    colouredImageExc[:,:,2]=std_normalize(excentricity,no_min=True)
    
    colouredImagearea=np.zeros(((Nx, Ny,3)))
    colouredImagearea[:,:,0]=theta
    colouredImagearea[:,:,1]=sat#area 
    colouredImagearea[:,:,2]=std_normalize(area,no_min=True)
    
    colouredImageDir=np.zeros(((Nx, Ny,3)))
    colouredImageDir[:,:,0]=theta
    colouredImageDir[:,:,1]=sat 
    colouredImageDir[:,:,2]=std_normalize(IntensityDeff,no_min=True) #1-np.exp(-IntensityDeff) 
    
    colouredImageExc=hsv_to_rgb(colouredImageExc)
    colouredImagearea=hsv_to_rgb(colouredImagearea)
    colouredImageDir=hsv_to_rgb(colouredImageDir)

    return {'dx': dx, 'dy': dy, 'phiFC': phiFC.real, 'phiK': phiK.real, 'absorption':absorption, 'Deff_xx': Deff_xx, 'Deff_yy': Deff_yy, 'Deff_xy': Deff_xy,  'excentricity': excentricity,'area':area, 'oriented_DF_exc': colouredImageExc, 'oriented_DF_area': colouredImagearea, 'oriented_DF_norm':colouredImageDir, 'theta':theta, 'local_orientation_strength':sat}




