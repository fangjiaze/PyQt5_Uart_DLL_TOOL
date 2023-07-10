import binascii




def remove_null_character(text):
    null_index = text.find('\0')

    if null_index != -1:
        return text[:null_index]
    else:
        return text


def lc_str2hex_print(str_data) :
    hex_data = binascii.hexlify(str_data.encode()).decode()
    formatted_hex_data = ' '.join(hex_data[i:i + 2] for i in range(0, len(hex_data), 2))
    print(formatted_hex_data)
    return formatted_hex_data

def lc_hex_print(byte_data) :
    hex_data = binascii.hexlify(byte_data).decode()
    formatted_hex_data = ' '.join(hex_data[i:i + 2] for i in range(0, len(hex_data), 2))
    print(formatted_hex_data)
    return formatted_hex_data