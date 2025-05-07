import os
from collections import Counter
import heapq
import pickle

class Node:
    def __init__(self, char=None, freq=0):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None
    def __lt__(self, other):
        return self.freq < other.freq

def build_huffman_tree(text):
    freq = Counter(text)
    heap = [Node(ch, fr) for ch, fr in freq.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = Node(freq=left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(heap, merged)
    return heap[0]

def build_codes(node, prefix="", code_map={}):
    if node:
        if node.char is not None:
            code_map[node.char] = prefix
        build_codes(node.left, prefix + "0", code_map)
        build_codes(node.right, prefix + "1", code_map)
    return code_map

def huffman_encode(text, code_map):
    return ''.join(code_map[ch] for ch in text)

def huffman_decode(encoded_text, tree):
    decoded = ""
    node = tree
    for bit in encoded_text:
        node = node.left if bit == '0' else node.right
        if node.char is not None:
            decoded += node.char
            node = tree
    return decoded

def bits_to_bytes(bitstring):
    b_array = bytearray()
    for i in range(0, len(bitstring), 8):
        byte = bitstring[i:i+8]
        b_array.append(int(byte.ljust(8, '0'), 2))
    return bytes(b_array)

def read_file_lines(filepath):
    with open(filepath, 'r') as f:
        return f.readlines()

def lcs_lines(X, Y):
    m, n = len(X), len(Y)
    dp = [["" for _ in range(n+1)] for _ in range(m+1)]
    for i in range(m):
        for j in range(n):
            if X[i] == Y[j]:
                dp[i+1][j+1] = dp[i][j] + X[i]
            else:
                dp[i+1][j+1] = max(dp[i+1][j], dp[i][j+1], key=len)
    return dp[m][n]

def get_diff_lines(X, Y, lcs_str):
    i = j = 0
    diff = ""
    for c in lcs_str.splitlines(keepends=True):
        while i < len(X) and X[i] != c:
            diff += f"- {X[i]}"
            i += 1
        while j < len(Y) and Y[j] != c:
            diff += f"+ {Y[j]}"
            j += 1
        i += 1
        j += 1
    diff += ''.join(f"- {line}" for line in X[i:])
    diff += ''.join(f"+ {line}" for line in Y[j:])
    return diff

# === Core Function Called from GUI ===
def process_files(fileA, fileB):
    X_lines = read_file_lines(fileA)
    Y_lines = read_file_lines(fileB)
    lcs_str = lcs_lines(X_lines, Y_lines)
    diff_result = get_diff_lines(X_lines, Y_lines, lcs_str)

    tree = build_huffman_tree(diff_result)
    codes = build_codes(tree)
    encoded = huffman_encode(diff_result, codes)

    base_name = os.path.splitext(os.path.basename(fileA))[0]
    bin_file = f"{base_name}_compressed.bin"
    tree_file = f"{base_name}_tree.pkl"
    txt_file = f"{base_name}_compressed_bits.txt"

    # Save encoded bits as bytes
    compressed_bytes = bits_to_bytes(encoded)
    with open(bin_file, "wb") as f_bin:
        f_bin.write(compressed_bytes)

    # Save Huffman tree separately
    with open(tree_file, "wb") as f_tree:
        pickle.dump(tree, f_tree)

    # Save readable bitstream
    with open(txt_file, "w") as f_txt:
        f_txt.write(encoded)

    # Decompression test (in-memory)
    decoded_text = huffman_decode(encoded, tree)
    status = decoded_text == diff_result

    stats = {
        'fileA_size': os.path.getsize(fileA),
        'fileB_size': os.path.getsize(fileB),
        'diff_size': len(diff_result.encode('utf-8')),
        'compressed_size': os.path.getsize(bin_file),
        'compression_ratio': (os.path.getsize(bin_file) / len(diff_result.encode('utf-8')) * 100) if diff_result else 0,
        'bin_file': bin_file,
        'tree_file': tree_file,
        'txt_file': txt_file
    }

    return diff_result, encoded, status, stats
