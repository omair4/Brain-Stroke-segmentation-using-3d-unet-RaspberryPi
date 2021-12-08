import os, time, re, glob
import h5py
import nibabel as nib
import numpy as np
from gpiozero import LED

def usb_inserted():

    devices = os.popen('sudo blkid').readlines()


    usbs = []
    for u in devices:
        loc = [u.split(':')[0]]
        if '/dev/sd' not in loc[0]: 
              continue # skip 
        loc+=re.findall(r'"[^"]+"',u)
        columns = ['loc']+re.findall(r'\b(\w+)=',u)
    
        usbs.append(dict(zip(columns,loc)))
        
        if len(usbs) > 0:
            flag = True
        if len(usbs) == 0:
            flag = False
        return flag

def standardize(image):

  standardized_image=np.zeros(image.shape)
  for c in range(image.shape[0]):
    for z in range(image.shape[3]):
      image_slice = image[c,:,:,z]
      centered = image_slice - np.mean(image_slice)
      if np.std(centered) != 0:
                centered_scaled = centered / np.std(centered)
      else:
        centered_scaled=centered
      standardized_image[c, :, :, z] = centered_scaled
  return standardized_image

def saveh5(filename,cbf_data,cbv_data,mtt_data,tmax_data):
    cbf_data=cbf_data.reshape(1,256,256,8)
    cbv_data=cbv_data.reshape(1,256,256,8)
    mtt_data=mtt_data.reshape(1,256,256,8)
    tmax_data=tmax_data.reshape(1,256,256,8)
    image_data=np.concatenate((cbf_data,cbv_data,mtt_data,tmax_data),axis=0)
    image_data = standardize(image_data)
    
    with h5py.File('/home/pi/brain_stroke/preprocess/'+str(filename),'w') as f:
        f.create_dataset("X_train",data=image_data)
    f.close()


####MAIN#############
print("Waiting for USB...")
led_r = LED(23)
led_g = LED(24)
while True:
    if usb_inserted():
        break
    else:
        led_r.on()
        time.sleep(0.5)
        led_r.off()
        time.sleep(0.5)
        
print("USB Inserted")
led_r.off()
time.sleep(2)

usb_path = glob.glob('/media/pi/*/')
print(f"USB Path:{usb_path[0]}")
files_in_usb = glob.glob(str(usb_path[0]) + '/*/')
print(f"Files in usb: {files_in_usb}")
files_in_usb = [i for i in files_in_usb if 'System' not in i]

#print(files_in_usb)

for file in files_in_usb:
    cbf_path = glob.glob(file+'/*CBF.*/*.nii')[0]
    cbv_path = glob.glob(file+'/*CBV.*/*.nii')[0]
    mtt_path = glob.glob(file+'/*MTT.*/*.nii')[0]
    tmax_path= glob.glob(file+'/*Tmax*/*.nii')[0]
    
    file = file.split('/')[-2]
    
    cbf_obj=nib.load(cbf_path)
    cbv_obj=nib.load(cbv_path)
    mtt_obj=nib.load(mtt_path)
    tmax_obj=nib.load(tmax_path)
    
    cbf = cbf_obj.get_fdata()
    cbv = cbv_obj.get_fdata()
    mtt = mtt_obj.get_fdata()
    tmax=tmax_obj.get_fdata()
    
    if cbf.shape[2] != 8:
        print(cbf.shape)
        if cbf.shape[2] > 8:
            n = cbf.shape[2]
            n = n - (n%8)
            for i in range(0,n):
                name = file + str(i)
                saveh5(name,cbf[:,:,(i*8):(i+1)*8],cbv[:,:,(i*8):(i+1)*8],mtt[:,:,(i*8):(i+1)*8],tmax[:,:,(i*8):(i+1)*8])
                
        if cbf.shape[2] < 8:
            while cbf.shape[2] <= 8:
                cbf = np.concatenate([cbf,cbf],axis=2)
                cbv = np.concatenate([cbv,cbv],axis=2)
                mtt = np.concatenate([mtt,mtt],axis=2)
                tmax= np.concatenate([tmax,tmax],axis=2)
            print(cbf.shape)                
            saveh5(file,cbf[:,:,:8],cbv[:,:,:8],mtt[:,:,:8],tmax[:,:,:8])
            
    if cbf.shape[2] == 8:
        saveh5(file,cbf,cbv,mtt,tmax)
        
        


    