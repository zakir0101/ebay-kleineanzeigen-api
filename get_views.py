from main import Main

api = Main(log=True, rotate_ip=True)
add_id = "2554816566"
add_detail = api.try_hard_get_add_views(add_id, True)
# try:
#     add_detail = api.try_hard_get_add_views(add_id,True)
# except Exception:
#     add_detail = api.html_text
print(add_detail)
