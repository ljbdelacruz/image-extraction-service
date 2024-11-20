# request_service.py
from .prisma_singleton import PrismaSingleton

def create_request(custom_id=None, base_image=None):
    prisma = PrismaSingleton.get_instance()
    data = {}
    if custom_id:
        data['id'] = custom_id
    if base_image:
        data['baseImage'] = base_image
    new_request = prisma.request.create({
        'data': data
    })
    return new_request

def create_image(cropped_image_path, request_id):
    prisma = PrismaSingleton.get_instance()
    new_image = prisma.image.create({
        'data': {
            'croppedImagePath': cropped_image_path,
            'requestId': request_id
        }
    })
    return new_image

def get_request(request_id):
    prisma = PrismaSingleton.get_instance()
    request_record = prisma.request.find_unique(where={'id': request_id}, include={'images': True})
    return request_record