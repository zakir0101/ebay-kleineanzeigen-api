# import execjs
# import js2py
# from mysterios_python import var
js_file = open("mysterius_function.js","r",encoding="utf-8").read()
js_file = js_file.replace("\n","")
open("mysterios_corrected2.js","w").write(js_file)
# js_file = open("mysterios_corrected.js","r").read()
# res_2 = js2py.eval_js(js_file)
# js2py.translate_file("mysterios_corrected.js", "mysterios_python.py")


# ctx = execjs.compile(js_file)

# Get the result of the JavaScript code
# jw = ctx.evlal('abcef')

# Print the result
# print(jw)
# jw = var.get("jw")
# string = "123456789"
# print("string",string)
# print("jw",jw(string))
