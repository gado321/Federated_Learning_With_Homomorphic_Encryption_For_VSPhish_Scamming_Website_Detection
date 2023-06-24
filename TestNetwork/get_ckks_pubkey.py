import socket
import ssl
import tenseal as ts

def create_ssl_context():
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.load_cert_chain(certfile="../servercert/server_cert.pem", keyfile="../servercert/server_key.pem")
    context.load_verify_locations(cafile="../servercert/root_cert.pem")
    context.cert_reqs = ssl.CERT_REQUIRED
    return context

def start_client():
    try:
        context = create_ssl_context()

        with socket.create_connection(('192.168.1.7', 12345)) as sock:
            with context.wrap_socket(sock, server_hostname='Key Generation Center') as ssock:
                len_serialized_public_key = int.from_bytes(ssock.recv(8), byteorder='big')
                serialized_public_key = bytearray()
                while len(serialized_public_key) < len_serialized_public_key:
                    chunk = ssock.recv(min(8192, len_serialized_public_key - len(serialized_public_key)))
                    serialized_public_key.extend(chunk)
                public_key = ts.context_from(bytes(serialized_public_key))

                print("Public key received successfully.")

            with open("public_key.bin", "wb") as f:
                f.write(public_key.serialize())

            print("Public key saved successfully.")
    except ssl.SSLError as e:
        print(f"SSL error occurred: {e}")
    except ssl.SSLCertVerificationError as e:
        print(f"SSL certificate verification error occurred: {e}")

if __name__ == "__main__":
    start_client()
