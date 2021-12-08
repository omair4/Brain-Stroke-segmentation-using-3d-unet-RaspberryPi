import boto3
from botocore.exceptions import NoCredentialsError
import glob
import os
import time

ACCESS_KEY = 'AKIAREDBHXOXJ3XW52WY'
SECRET_KEY = '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'


def upload_to_aws(local_file, bucket, s3_file):
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)

    try:
        s3.upload_file(local_file, bucket, s3_file,ExtraArgs={'ACL':'public-read'})
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False


folder_path = glob.glob('/home/pi/brain_stroke/outputs/*/')[0]
folder=folder_path.split('/')[-2]

files_path = glob.glob(folder_path+"*")

usb_path = glob.glob('/media/pi/*/')[0]
os.mkdir(usb_path+'outputs/')
usb_path = usb_path + 'outputs/'

for file in files_path:
    filename = file.split('/')[-1]
    os.system('cp '+file+' '+usb_path)
    upload = upload_to_aws(file,'brainstroke',str(folder)+'/'+str(filename))
    if not upload:
        print(f"{filename} didn't upload")
from gpiozero import LED
led_r = LED(23)
led_g = LED(24)

led_r.off()
led_g.on()

time.sleep(5)
