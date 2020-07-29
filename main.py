from PIL import Image


def string_to_bin_chain(message_string):
    chain = list()
    for character in message_string:
        binary_string = '{0:08b}'.format(ord(character))
        for value in binary_string:
            chain.append(int(value))
    return chain


def bin_chain_to_string(chain, secure_anchor):
    message_string = ''
    chain_pointer = 0
    while chain_pointer + 8 <= len(chain):
        binary_string = ''.join(str(x) for x in chain[chain_pointer:chain_pointer + 8])
        message_string += chr(int(binary_string, 2))
        chain_pointer += 8
        if len(message_string) > len(secure_anchor) and message_string[-(len(secure_anchor)):] == secure_anchor:
            break
    return message_string[:-(len(secure_anchor))]


def encode_pixel(rgba_tuple, message_slice):
    binary_red = '{0:08b}'.format(rgba_tuple[0])[:7] + str(message_slice[0])
    binary_green = '{0:08b}'.format(rgba_tuple[1])[:7] + str(message_slice[1])
    binary_blue = '{0:08b}'.format(rgba_tuple[2])[:7] + str(message_slice[2])
    binary_alpha = '{0:08b}'.format(rgba_tuple[3])[:7] + str(message_slice[3])
    return (
        int(binary_red, base=2),
        int(binary_green, base=2),
        int(binary_blue, base=2),
        int(binary_alpha, base=2)
    )


def decode_pixel(rgba_tuple):
    binary_red = int('{0:08b}'.format(rgba_tuple[0])[-1], base=2)
    binary_green = int('{0:08b}'.format(rgba_tuple[1])[-1], base=2)
    binary_blue = int('{0:08b}'.format(rgba_tuple[2])[-1], base=2)
    binary_alpha = int('{0:08b}'.format(rgba_tuple[3])[-1], base=2)
    return [binary_red, binary_green, binary_blue, binary_alpha]


def load_text(text_path, secure_anchor):
    with open(text_path, 'r', encoding='utf-8') as f:
        text = f.read()
    text += secure_anchor
    return text


def encode_image(image_path, text_path, save_path, secure_anchor='++++++++++'):
    im = Image.open(image_path)
    im = im.convert("RGBA")
    pixel_tuples = im.getdata()
    message = load_text(text_path, secure_anchor)
    message_chain = string_to_bin_chain(message)
    message_pointer = 0
    new_pixel_tuples = list()
    for pixel_item in pixel_tuples:
        if message_pointer != len(message_chain):
            new_pixel_tuples.append(encode_pixel(pixel_item, message_chain[message_pointer:message_pointer + 4]))
            message_pointer += 4
        else:
            new_pixel_tuples.append(pixel_item)
    im.putdata(new_pixel_tuples)
    im.save(save_path, "PNG")


def decode_image(image_path, secure_anchor='++++++++++'):
    im = Image.open(image_path)
    im = im.convert("RGBA")
    pixel_tuples = im.getdata()
    message_chain = list()
    for pixel_item in pixel_tuples:
        message_chain_list = decode_pixel(pixel_item)
        message_chain.append(message_chain_list[0])
        message_chain.append(message_chain_list[1])
        message_chain.append(message_chain_list[2])
        message_chain.append(message_chain_list[3])
    return bin_chain_to_string(message_chain, secure_anchor)


# Program start
encode_image('cat.png', 'text.txt', 'cat1.png')
print(decode_image('cat1.png'))
