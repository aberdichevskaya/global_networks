# %%
import socket
import pickle
import copy

# %%
def return_to_null(bitlist):
    result = copy.deepcopy(bitlist)
    i = 1
    leng = len(bitlist)
    while i <= leng:
        result[i-1] = 0
        i *= 2
    return result

# %%
def check_for_mistakes(received, recounted):
    leng = len(received)
    cnt = 0
    i = 1
    while i <= leng:
        if received[i-1] != recounted[i-1]:
            cnt += i
        i *= 2
    if cnt == 0:
        return [0]
    elif cnt <= leng:
        received[cnt-1] == 0 if received[cnt-1] else 1
        return [1, cnt]
    else:
        return [2]

# %%
def hemming_decode(binary_list):
    sz = len(binary_list)
    coded_list = []
    mistake_num = []
    for _ in range(sz):
        coded_list.append(return_to_null(binary_list[_]))
        i = 1
        leng = len(coded_list[_])
        while i <= leng:
            cnt = 0
            j = i-1
            while j <= leng:
                for a in range(j, min(j+i, leng)):
                    cnt += coded_list[_][a]
                j += 2*i
            coded_list[_][i-1] = cnt % 2
            i *= 2
        mistake_num.append(check_for_mistakes(binary_list[_], 
                                                  coded_list[_]))
    return mistake_num

# %%


# %%
if __name__ == "__main__":
    host = '127.0.0.1'
    port = 8
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(1)
    print('Слушаю порт номер ', port)
    conn, addr = sock.accept()
    while True:
        request = b""
        while True:
            data = conn.recv(1024)
            request += data
            if len(data) < 1024:
                break
        message = pickle.loads(request)
        mistakes = hemming_decode(message)
        conn.send(pickle.dumps(mistakes))
    conn.close()

# %%
