from score_api import function_handler, load_model

load_model('../models')

event = { "bucket": "virtual-concierge-frames-ap-southeast-2", "key": "faces/7_26/20_50/1532652558_0.jpg" }
print(function_handler(event, None))
