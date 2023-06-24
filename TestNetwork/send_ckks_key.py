import socket
import ssl
import tenseal as ts

def create_ssl_context():
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile="../keys/root_cert.pem", keyfile="../keys/root_key.pem")
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_verify_locations(cafile="../keys/root_cert.pem")
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
                    client_cert = conn.getpeercert()
                    if client_cert:
                        cn = None
                        for sub in client_cert['subject']:
                            for k, v in sub:
                                if k == 'commonName':
                                    cn = v
                                    break
                            if cn:
                                break
                        if cn == 'Agent':
                            # Handle the case where the client CN is 'Agent'
                            len_serialized_context = len(ckks_context.serialize()).to_bytes(8, byteorder='big')
                            conn.sendall(len_serialized_context)
                            conn.sendall(ckks_context.serialize())
                            print(f"Sent key pair to client with CN 'Agent' from {addr[0]}")
                        elif cn == 'Server':
                            # Handle the case where the client CN is 'Server'
                            # Send the public key only
                            pub_context = ckks_context.copy()
                            public_key = pub_context.make_context_public()
                            len_serialized_key = len(public_key.serialize()).to_bytes(8, byteorder='big')
                            conn.sendall(len_serialized_key)
                            conn.sendall(public_key.serialize())
                            print(f"Sent public key to client with CN 'Server' from {addr[0]}")
                        else:
                            print(f"Unknown client CN '{cn}' from {addr[0]}")
                    else:
                        print(f"No client certificate presented by {addr[0]}")
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
    start_kgc_server(ckks_context)