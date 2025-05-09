import serial
import time

def send_command_and_wait_ok(ser, command, timeout=1.9):
    ser.reset_input_buffer()
    ser.write(command.encode())
    print(f"\nCommande envoyée : {command.strip()}")

    start_time = time.time()
    response = ""

    while time.time() - start_time < timeout:
        if ser.in_waiting > 0:
            line = ser.readline().decode(errors='ignore').strip()
            if line:
                print(">>", line)
                response += line + "\n"
                if "OK" in line:
                    return True
        time.sleep(0.015)
    
    print("Réponse non reçue ou incomplète.")
    return False

def wait_for_arrow_prompt(ser, timeout=1.9):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if ser.in_waiting > 0:
            line = ser.readline().decode(errors='ignore').strip()
            if ">" in line:
                return True
        time.sleep(0.02)
    return False

def send_data_in_chunks(ser, file_path):
    try:
        with open(file_path, 'rb') as file:
            data = file.read()
            chunk_size = 255
            chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
            for i, chunk in enumerate(chunks):
                cmd = f"AT+BLEGATTCWR=0,4,5,,{len(chunk)}\r\n"
                ser.write(cmd.encode())
                if not wait_for_arrow_prompt(ser, timeout=1):
                    break
                ser.write(chunk)
                time.sleep(0.15)
                print(i + 1)
    except FileNotFoundError:
        print(f"Erreur : Fichier non trouvé : {file_path}")

try:
    ser = serial.Serial('COM5', 115200, timeout=0.014)
    time.sleep(0.014)
    
    if send_command_and_wait_ok(ser, "AT+BLEINIT=1\r\n"):
       if send_command_and_wait_ok(ser, 'AT+BLECONN=0,"08:3A:8D:02:12:3E"\r\n'):
            if send_command_and_wait_ok(ser, "AT+BLEGATTCPRIMSRV=0\r\n"):
               if send_command_and_wait_ok(ser, "AT+BLEGATTCCHAR=0,4\r\n"):
                    if send_command_and_wait_ok(ser, "AT+BLECFGMTU=0,514\r\n"):
                        ser.write(b"AT+BLEGATTCWR=0,4,2,,10\r\n")
                        if wait_for_arrow_prompt(ser):
                            ser.write(bytes([0x00, 0x00, 0x6A, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))
                            time.sleep(4)
                            
                            ser.write(b"AT+BLEGATTCWR=0,4,2,,10\r\n")
                            if wait_for_arrow_prompt(ser):
                                ser.write(bytes([0x00, 0x00, 0x28, 0x23, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))
                                time.sleep(4)
                                ser.write(b"AT+BLEGATTCWR=0,4,5,,5\r\n")
                                if wait_for_arrow_prompt(ser):
                                    ser.write(bytes([0x02, 0x38, 0x96, 0x04, 0x00]))
                                    time.sleep(4)   
                                    
    send_data_in_chunks(ser, 'HMI_V4_For_CI2802_v4.2.4_nBOOTLOADER.bin')
    

except serial.SerialException as e:
    print(f"Erreur série : {e}")

finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Port série fermé.")
