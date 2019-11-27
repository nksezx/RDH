from PIL import Image
import numpy as np

img = Image.open("./lena.bmp")
img = np.array(img)

img_len = 512
block_len = 32
block_num_in_a_row = img_len // block_len
block_num = (img_len / block_len) ** 2
pixel_in_a_block = block_len ** 2

data = '101111000010101001010101011111000100001000101111010101000100110111001110'
curr_index = 0


def get_value(elem):
    return elem[0]


summit = []
for i in range(block_num_in_a_row):
    summit.append([-1] * block_num_in_a_row)


def process_block(block_x, block_y):
    global curr_index
    left_top_point = (block_x * block_len, block_y * block_len)

    # sort pixels, get the middle position
    pixel_list = []
    x0 = left_top_point[0]
    y0 = left_top_point[1]
    for i in range(block_len):
        for j in range(block_len):
            x = x0 + i
            y = y0 + j
            value = img[x][y]
            pixel_list.append((value, x, y))
    pixel_list.sort(key=get_value)
    middle_value = pixel_list[pixel_in_a_block // 2][0]

    # get value of difference-histogram summit
    histogram = [0 for _ in range(260)]
    for i in range(pixel_in_a_block):
        diff = abs(int(pixel_list[i][0]) - int(middle_value))
        histogram[diff] += 1
    summit_diff = histogram.index(max(histogram))
    summit[block_x][block_y] = summit_diff

    # change every pixel
    for i in range(pixel_in_a_block):
        if curr_index == len(data):
            return
        diff = int(pixel_list[i][0]) - int(middle_value)
        x = pixel_list[i][1]
        y = pixel_list[i][2]
        if i < pixel_in_a_block // 2:
            if diff < -summit_diff:
                img[x][y] -= 1
            elif diff == -summit_diff:
                if data[curr_index] == '1':
                    img[x][y] -= 1
                curr_index += 1
        elif i > pixel_in_a_block // 2:
            if diff > summit_diff:
                img[x][y] += 1
            elif diff == summit_diff:
                if data[curr_index] == '1':
                    img[x][y] += 1
                curr_index += 1


# Encryption of data
for i in range(int(block_num_in_a_row)):
    if curr_index == len(data):  # rough coding
        break
    for j in range(int(block_num_in_a_row)):
        if curr_index == len(data):
            break
        process_block(i, j)

with open("lena_with_data.bmp", "wb") as fp:
    Image.fromarray(img).save(fp)

# decryption of data
img_with_data = Image.open("./lena_with_data.bmp")
img_with_data = np.array(img_with_data)

data_extracted = []


def recover_block(block_x, block_y, summit_diff):
    left_top_point = (block_x * block_len, block_y * block_len)

    # get the right order
    pixel_list = []
    x0 = left_top_point[0]
    y0 = left_top_point[1]
    for i in range(block_len):
        for j in range(block_len):
            x = x0 + i
            y = y0 + j
            value = img_with_data[x][y]
            pixel_list.append((value, x, y))
    pixel_list.sort(key=get_value)
    middle_value = pixel_list[pixel_in_a_block // 2][0]

    count = 0
    # change and sort again
    for i in range(pixel_in_a_block):
        diff = int(pixel_list[i][0]) - int(middle_value)
        x = pixel_list[i][1]
        y = pixel_list[i][2]
        if i < pixel_in_a_block // 2:
            if diff == - summit_diff - 1:
                pixel_list[i] = (pixel_list[i][0]+1, x, y)
                count += 1
        elif i > pixel_in_a_block // 2:
            if diff == summit_diff + 1:
                pixel_list[i] = (pixel_list[i][0]-1, x, y)
                count += 1
    pixel_list.sort(key=get_value)

    # recover and extract data
    for i in range(pixel_in_a_block):
        if len(data_extracted) == len(data):
            return
        x = pixel_list[i][1]
        y = pixel_list[i][2]
        diff = int(img_with_data[x][y]) - int(middle_value)
        if i < pixel_in_a_block // 2:
            if diff < - summit_diff - 1:
                img_with_data[x][y] += 1
            elif diff == - summit_diff - 1:
                img_with_data[x][y] += 1
                data_extracted.append((x, y, '1'))
            elif diff == - summit_diff:
                data_extracted.append((x, y, '0'))
        elif i > pixel_in_a_block // 2:
            if diff > summit_diff + 1:
                img_with_data[x][y] -= 1
            elif diff == summit_diff + 1:
                img_with_data[x][y] -= 1
                data_extracted.append((x, y, '1'))
            elif diff == summit_diff:
                data_extracted.append((x, y, '0'))


for i in range(int(block_num_in_a_row)):
    for j in range(int(block_num_in_a_row)):
        if summit[i][j] == -1:
            continue
        recover_block(i, j, summit[i][j])

data_extracted.sort()
answer = []
for i in range(len(data_extracted)):
    answer.append(data_extracted[i][2])
print(''.join(answer))
with open("lena_recovered.bmp", "wb") as fp:
    Image.fromarray(img_with_data).save(fp)
