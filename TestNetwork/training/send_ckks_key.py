import socket
import ssl
import tenseal as ts

def create_ssl_context():
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile="../keys/root_cert.pem", keyfile="../keys/root_key.pem")
    return context

def create_ckks_keys():
    context = ts.context(ts.SCHEME_TYPE.CKKS, poly_modulus_degree=8192, coeff_mod_bit_sizes=[40, 21, 21, 21, 40])
    context.global_scale = pow(2, 21)
    context.generate_galois_keys()
    return context

def start_kgc_server(ckks_context):
    print("Starting KGC server...")
    context = create_ssl_context()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
        sock.bind(('0.0.0.0', 12345))
        sock.listen(5)
        with context.wrap_socket(sock, server_side=True) as ssock:
            while True:
                conn, addr = None, None
                try:
                    conn, addr = ssock.accept()
                    len_serialized_context = len(ckks_context.serialize()).to_bytes(8, byteorder='big')
                    conn.sendall(len_serialized_context)
                    conn.sendall(ckks_context.serialize())
                    print(f"Client connected from {addr[0]}")
                except ssl.SSLError as e:
                    if addr:
                        print(f"SSL error occurred from client {addr[0]}: {e}")
                    else:
                        print(f"SSL error occurred: {e}")
                except Exception as e:
                    print(f"An error occurred from client {addr[0]}: {e}")
                finally:
                    # Close the connection to the client
                    if conn:
                        conn.close()

    print("KGC server stopped.")

if __name__ == "__main__":
    ckks_context = create_ckks_keys()
    print(ckks_context)
    start_kgc_server(ckks_context)

                  