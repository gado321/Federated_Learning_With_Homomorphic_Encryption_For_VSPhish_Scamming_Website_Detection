import socket
import ssl
import tenseal as ts

def create_ssl_context():
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.load_cert_chain(certfile="../clientkey/client_cert.pem", keyfile="../clientkey/client_key.pem")
    context.load_verify_locations(cafile="../clientkey/root_cert.pem")
    return context

def start_client():
    try:
        context = create_ssl_context()

        with socket.create_connection(('172.26.0.6', 12345)) as sock:
            with context.wrap_socket(sock, server_hostname='localhost') as ssock:
                len_serialized_context = int.from_bytes(ssock.recv(8), byteorder='big')
                serialized_context = bytearray()
                while len(serialized_context) < len_serialized_context:
                    chunk = ssock.recv(min(8192, len_serialized_context - len(serialized_context)))
                    serialized_context.extend(chunk)
                ckks_context = ts.context_from(bytes(serialized_context))

                print("CKKS context received successfully.")

            with open("ckks_context.bin", "wb") as f:
                f.write(ckks_context.serialize())

            print("CKKS context saved successfully.")
    except ssl.SSLError as e:
        print(f"SSL error occurred: {e}")
    except ssl.SSLCertVerificationError as e:
        print(f"SSL certificate verification error occurred: {e}")

if __name__ == "__main__":
    start_client()
