def ProcessPrice(str):
    i = 0
    str_price = ''
    while ord(str[i]) > 57 or ord(str[i]) < 48:
        i += 1
    
    while i < len(str) and ord(str[i]) <= 57 and ord(str[i]) >= 48:
        str_price += str[i]
        i += 1
    return str_price

ttt = '5000'
print(ProcessPrice(ttt))