import requests



html = requests.get("https://www.baidu.com/bh/dict/ydxx_8470845393997983874?from=dicta&sf_ref=med_pc&sf_ch=ch_med_pc")
print(html.text)