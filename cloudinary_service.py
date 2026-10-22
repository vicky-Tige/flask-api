import cloudinary
import cloudinary.uploader
Cloud_name='e23erfxz'
Api_key='698831731941554'
Secret_key='vbGhialZ_Lg3xBuxqavq70g1Np4'
# connecting to cloudinary
cloudinary.config(
    cloud_name=Cloud_name,
    api_key=Api_key,
    api_secret=Secret_key
)
def upload_pdf(pdf_file):
    try:
        file_path=f'receipts/{pdf_file}.pdf'
        # upload pdf
        upload= cloudinary.uploader.upload(file_path,resource_type='raw')
        
        receipt_url=upload['secure_url']

        print(receipt_url)
        print("Successfull file upload")
        return 'success'
    except Exception as e:
        print(f'upload failed: {e}')
        return 'failed'


    
# import cloudinary
# import cloudinary.uploader

# Cloud_Name="e23erfxz"
# Api_Key="698831731941554"
# Secret_Key="*********************************"

# #connecting to cloudary
# cloudinary.config(
#     cloud_name=Cloud_Name,
#     api_Key=Api_Key,
#     api_secret=Secret_Key
# )
# # print("cloudinary configuration successfully")
# def upload_pdf(pdf_file):
#     print("upload_pdf function has started-----------")
#     try:
#        file_path=f"receipts/{pdf_file}.pdf"
#        #upload a pdf
#        upload=cloudinary.uploader.upload(file_path,resource_type="raw")
#        receipt_url=upload["secure_url"]

#        print(receipt_url)
#        print("successfully cloudary uploaded")
#        return "receipt_url"

#     except Exception as e:
#         print(f"upload failed:{e}")
#         print("failed")
