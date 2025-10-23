from pymodbus.client import ModbusSerialClient
import time
import threading
from queue import Queue
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Matplotlib 백엔드 설정
matplotlib.use('TkAgg')

class MotorController:
    def __init__(self, port="/dev/ttyUSB1", baudrate=115200, device_id=100):
        self.client = ModbusSerialClient(
            port=port,
            baudrate=baudrate,
            bytesize=8,
            parity="N",
            stopbits=1,
            timeout=0.1,
        )
        self.device_id = device_id
        self.lock = threading.Lock()

    def connect(self):
        return self.client.connect()

    def close(self):
        self.set_speed(0)
        self.client.close()

    def read_register(self, address, count=1):
        try:
            with self.lock:
                response = self.client.read_holding_registers(
                    address=address, count=count, slave=self.device_id
                )
            if response and not response.isError():
                return response.registers
            return None
        except:
            return None

    def write_register(self, address, value):
        try:
            with self.lock:
                response = self.client.write_register(
                    address=address, value=value, slave=self.device_id
                )
            if response and not response.isError():
                return True
            return False
        except:
            return False

    def set_speed(self, speed):
        if 0 <= speed <= 100:
            return self.write_register(0x0001, speed)
        return False

    def set_cw_ccw(self, direction):
        if direction in [0, 1]:
            return self.write_register(0x0002, direction)
        return False

    def set_enable(self, enable):
        if enable in [0, 1]:
            return self.write_register(0x0003, enable)
        return False

    def set_brake(self, brake):
        if brake in [0, 1]:
            return self.write_register(0x0004, brake)
        return False

    def get_current_RPM(self):
        return self.read_register(0x0015)


def user_input_handler(motor, run_event, input_queue):
    while run_event.is_set():
        try:
            user_input = input()
            if user_input.isdigit():
                user_speed = int(user_input)
                if 0 <= user_speed <= 100:
                    input_queue.put(user_speed)
            else:
                run_event.clear()
                break
        except:
            run_event.clear()
            break
        
def motor_control(motor, run_event, direction_lock, current_direction, input_queue):
    while run_event.is_set():
        if not input_queue.empty():
            new_speed = input_queue.get()
            motor.set_speed(new_speed)

        current_rpm = motor.get_current_RPM()
        if current_rpm:
            rpm_value = current_rpm[0]
            if rpm_value == 0:
                motor.set_enable(0)
                with direction_lock:
                    current_direction[0] = 1 - current_direction[0]
                    motor.set_cw_ccw(current_direction[0])
                motor.set_enable(1)
        time.sleep(0.5)


def plot_rpm(motor, run_event, run_time=20):
    x_data = []
    y_data = []
    start_time = time.time()

    fig, ax = plt.subplots()
    line, = ax.plot([], [], 'b-')
    ax.set_xlim(0, run_time)
    ax.set_ylim(-10, 2000)
    ax.set_xlabel("Time (sec)")
    ax.set_ylabel("RPM")
    ax.set_title("Real-time Motor RPM")

    def update(frame):
        if not run_event.is_set():
            plt.close()
            return line,
        current_time = time.time() - start_time
        if current_time > run_time:
            ax.set_xlim(current_time - run_time, current_time)
        else:
            ax.set_xlim(0, run_time)

        current_register = motor.get_current_RPM()
        if current_register:
            rpm_value = current_register[0]
            x_data.append(current_time)
            y_data.append(rpm_value)
            line.set_data(x_data, y_data)
        return line,

    ani = FuncAnimation(fig, update, interval=1000, blit=False, save_count=100)
    try:
        plt.show()
    except:
        pass
    run_event.clear()


if __name__ == "__main__":
    motor = MotorController()

    if not motor.connect():
        print("[오류] Modbus 연결 실패")
        exit()
    else:
        print("모터 연결")
    start_time = time.time()
    if not motor.set_speed(50):
        print("[오류] 속도 설정 실패")
    else:
        print("속도 설정 성공")

    
    if not motor.set_brake(0):
        print("[오류] 브레이크 해제 실패")
    end_time = time.time()
    print(end_time - start_time)

    if motor.connect():
        run_event = threading.Event()
        run_event.set()
        direction_lock = threading.Lock()
        current_direction = [0]
        input_queue = Queue()

        motor_thread = threading.Thread(
            target=motor_control, args=(motor, run_event, direction_lock, current_direction, input_queue)
        )

        motor_thread.start()

        try:
            plot_rpm(motor, run_event, run_time=20)
        except:
            run_event.clear()

        motor_thread.join()

        motor.close()
