# **CHACHA20**

# LIBRARIES
import struct
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np
#-------------------------------------------------------------------------------

# CHACHA20 IMPLEMENTATION

def yield_chacha20_xor_stream(key, iv, position,method):
  """Generate the xor stream with the ChaCha20 cipher."""
  if not isinstance(position, int):
    raise TypeError
  if position & ~0xffffffff:
    raise ValueError('Position is not uint32.')
  if not isinstance(key, bytes):
    raise TypeError
  if not isinstance(iv, bytes):
    raise TypeError
  if len(key) != 32:
    raise ValueError
  if len(iv) != 12:
    raise ValueError

  def rotate(v, c):
    return ((v << c) & 0xffffffff) | v >> (32 - c)

  def quarter_round(x, a, b, c, d):
    x[a] = (x[a] + x[b]) & 0xffffffff
    x[d] = rotate(x[d] ^ x[a], 16)
    x[c] = (x[c] + x[d]) & 0xffffffff
    x[b] = rotate(x[b] ^ x[c], 12)
    x[a] = (x[a] + x[b]) & 0xffffffff
    x[d] = rotate(x[d] ^ x[a], 8)
    x[c] = (x[c] + x[d]) & 0xffffffff
    x[b] = rotate(x[b] ^ x[c], 7)

  ctx = [0] * 16
  ctx[:4] = (1634760805, 857760878, 2036477234, 1797285236)
  ctx[4 : 12] = struct.unpack('<8L', key)
  ctx[12] = position
  ctx[13 : 16] = struct.unpack('<3L', iv)
  x = list(ctx)
  for i in range(10):
      if method != 1:
          if method != 3: quarter_round(x, 0, 4,  8, 12)
          quarter_round(x, 1, 5,  9, 13)
          quarter_round(x, 2, 6, 10, 14)
          quarter_round(x, 3, 7, 11, 15)
      if method != 2:
          if method != 3: quarter_round(x, 0, 5, 10, 15)
          quarter_round(x, 1, 6, 11, 12)
          quarter_round(x, 2, 7,  8, 13)
          quarter_round(x, 3, 4,  9, 14)
  for c in struct.pack('<16L', *(
    (x[i] + ctx[i]) & 0xffffffff for i in range(16))):
    yield c


def chacha20_encrypt(data, key, iv, position, method):
  """Encrypt (or decrypt) with the ChaCha20 cipher."""
  if not isinstance(data, bytes):
    raise TypeError
  if iv is None:
    iv = b'\0' * 12
  if isinstance(key, bytes):
    if not key:
      raise ValueError('Key is empty.')
    if len(key) < 32:
      # TODO(pts): Do key derivation with PBKDF2 or something similar.
      key = (key * (32 // len(key) + 1))[:32]
    if len(key) > 32:
      raise ValueError('Key too long.')

  return bytes(a ^ b for a, b in
      zip(data, yield_chacha20_xor_stream(key, iv, position,method)))
#-------------------------------------------------------------------------------

# AUXILIAR FUNCTIONS

def generate_plot(data, mthd, method):
    '''
    Function that generates the histograms and stores them
    with the proper filename.
    '''

    plt.style.use("ggplot")

    data_plot = pd.Series(data)
    fig, ax = plt.subplots(figsize = (12,10))

    if mthd == 1:
        data_plot.plot(kind = "hist", alpha = 0.65,bins = max(data)-min(data),align = "left",color = "#348ABD")
        data_plot.plot(kind = "kde",linewidth = 2,secondary_y = True)
        # Aesthetic modifications
        ax.right_ax.set_ylabel("Density")
        ax.right_ax.yaxis.set_major_formatter(PercentFormatter(xmax=1))
        ax.right_ax.grid(False)
        ax.right_ax.tick_params(right = False)
        ax.set_xlim(min(data),max(data))
        x_lab = "Number of bits"
        title = "Frequency/density of total number of modified bits"
        filename = "mod_bits"
        bbox = "tight"
    else:
        data_plot.plot(kind = "bar",color = "#348ABD")
        x_lab = "Bit positions"
        title = "Frequency of position modifications"
        ax.set_xticks(np.arange(0,512,8))
        filename = "mod_pos"
        bbox = None

    #  Aesthetic modificactions.
    if method == 1: filename += "_without_columns"
    elif method == 2: filename += "_without_diagonals"
    elif method == 3: filename += "_without_specific"
    ax.set_xlabel(x_lab)
    ax.set_ylabel("Frequencies")
    ax.set_title(title)
    ax.yaxis.grid(True)
    ax.tick_params(direction='out')
    ax.set_title(title,size = 17,pad = 10)
    plt.savefig("./Images/"+filename+".png",bbox_inches = bbox)
#-------------------------------------------------------------------------------

# MAIN FUNCTIONS

def histograms(key,nonce,method):
  '''
  Function that computes the number of different bits in comparsion to the
  cyphertext with Counter = 1 as well as the positions that have been modified.
  '''
  n_mod_bits = []
  n_mod_pos = [0]*512
  # Obtaining the cypertext with Counter = 1.
  reference = chacha20_encrypt(bytes(64),key,nonce,1, method)
  aux_ref = []
  aux_ref_str = ''.join([bin(x)[2:].zfill(8) for x in reference])
  aux_ref[:0] = aux_ref_str
  aux_ref = [int(x) for x in aux_ref]
  # Performing the comparisons.
  for i in range(2,4097):
      n_mod_bits_i = 0
      encripted = chacha20_encrypt(bytes(64),key,nonce,i, method)
      aux = []
      aux_str = ''.join([bin(x)[2:].zfill(8) for x in encripted])
      aux[:0] = aux_str
      aux = [int(x) for x in aux]
      for j in range(512):
          if aux[j] != aux_ref[j]:
              n_mod_pos[j] += 1
              n_mod_bits_i += 1
      n_mod_bits.append(n_mod_bits_i)
  generate_plot(n_mod_bits,1,method)
  generate_plot(n_mod_pos,2,method)

def main():
    key = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f'
    nonce = b'\x00\x00\x00\x09\x00\x00\x00\x4a\x00\x00\x00\x00'
    # Normal Chacha20 execution.
    histograms(key,nonce,0)
    # Chacha20 without Column rounds.
    histograms(key,nonce,1)
    # Chaha20 without Diagonal rounds.
    histograms(key,nonce,2)
    # Chacha20 without specific rounds.
    histograms(key,nonce,3)
main()
