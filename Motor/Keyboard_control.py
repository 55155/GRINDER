from pymodbus.client import ModbusSerialClient
import time
import threading
from queue import Queue
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


class MotorController:
    def __init__(self, port="/dev/ttyUSB0", baudrate=115200, device_id=100):
        """
        모터 컨트롤러 초기화
        :param port: USB 포트 경로
        :param baudrate: 통신 속도
        :param device_id: Device ID
        """
        self.client = ModbusSerialClient(
            port=port,
            baudrate=baudrate,
            bytesize=8,
            parity="N",
            stopbits=1,
            timeout=1,
        )
        self.device_id = device_id
        self.lock = threading.Lock()

    def connect(self):
        """MODBUS-RTU 연결"""
        return self.client.connect()

    def close(self):
        """연결 종료"""
        self.client.close()

    def read_register(self, address, count=1):
        """
        레지스터 읽기
        :param address: 시작 레지스터 주소
        :param count: 읽을 레지스터 개수
        :return: 읽은 데이터 리스트
        """
        try:
            with self.lock:
                response = self.client.read_holding_registers(
                    address=address, count=count, slave=self.device_id
                )
            if response and not response.isError():
                return response.registers
            else:
                print(f"[오류] 레지스터 {hex(address)} 읽기 실패")
                return None
        except Exception as e:
            print(f"[예외] 레지스터 읽기 중 오류 발생: {e}")
            return None

    def write_register(self, address, value):
        """
        레지스터 쓰기
        :param address: 대상 레지스터 주소
        :param value: 쓰기 값
        :return: 성공 여부
        """
        try:
            with self.lock:
                response = self.client.write_register(
                    address=address, value=value, slave=self.device_id
                )
            if response and not response.isError():
                return True
            else:
                print(f"[오류] 레지스터 {hex(address)} 쓰기 실패")
                return False
        except Exception as e:
            print(f"[예외] 레지스터 쓰기 중 오류 발생: {e}")
            return False

    def set_speed(self, speed):
        """속도 설정 (0-100)"""
        if 0 <= speed <= 100:
            return self.write_register(0x0001, speed)
        else:
            print("[오류] 속도는 0에서 100 사이여야 합니다.")
            return False

    def set_cw_ccw(self, direction):
        """CW/CCW 설정"""
        if direction in [0, 1]:
            return self.write_register(0x0002, direction)
        else:
            print("[오류] 방향 값은 0(CW) 또는 1(CCW)이어야 합니다.")
            return False

    def set_enable(self, enable):
        """모터 활성화/비활성화"""
        if enable in [0, 1]:
            return self.write_register(0x0003, enable)
        else:
            print("[오류] 활성화 값은 0(비활성화) 또는 1(활성화)이어야 합니다.")
            return False

    def set_brake(self, brake):
        """브레이크 설정"""
        if brake in [0, 1]:
            return self.write_register(0x0004, brake)
        else:
            print("[오류] 브레이크 값은 0(OFF) 또는 1(ON)이어야 합니다.")
            return False

    def get_current_RPM(self):
        """현재 RPM 읽기"""
        return self.read_register(0x0015)


def user_input_handler(motor, run_event, input_queue):
    """
    사용자로부터 속도 입력을 비동기로 받는 함수
    """
    while not run_event.is_set():
        try:
            user_speed = input("[입력] 속도를 입력하세요 (0-100): ")
            if not user_speed.isdigit():
                print("[오류] 숫자를 입력하세요.")
                continue
            user_speed = int(user_speed)
            if 0 <= user_speed <= 100:
                input_queue.put(user_speed)
                print(f"[설정] 속도가 {user_speed}로 설정되었습니다.")
            else:
                print("[오류] 속도는 0에서 100 사이여야 합니다.")
        except KeyboardInterrupt:
            print("[입력] 사용자 입력 중단")
            run_event.set()
            break


def motor_control(motor, run_event, direction_lock, current_direction, input_queue):
    """
    사용자 입력 큐를 확인하며, 입력된 속도를 모터에 반영하는 함수
    """
    while not run_event.is_set():
        if not input_queue.empty():
            new_speed = input_queue.get()
            motor.set_speed(new_speed)
            print(f"[제어] 속도를 {new_speed}로 설정했습니다.")

        current_rpm = motor.get_current_RPM()
        if current_rpm:
            rpm_value = current_rpm[0]
            print(f"[제어] 현재 RPM: {rpm_value}")
            if rpm_value == 0:
                print("[제어] RPM이 0입니다. 방향을 반전합니다.")
                motor.set_enable(0)
                with direction_lock:
                    current_direction[0] = 1 - current_direction[0]
                    motor.set_cw_ccw(current_direction[0])
                motor.set_enable(1)
        time.sleep(0.5)


def plot_rpm(motor, run_event, run_time=20):
    """
    실시간 RPM 플로팅
    """
    x_data = []
    y_data = []
    start_time = time.time()

    fig, ax = plt.subplots()
    line, = ax.plot([], [], 'b-', label="RPM")
    ax.set_xlim(0, run_time)
    ax.set_ylim(0, 1000)
    ax.set_xlabel("시간 (초)")
    ax.set_ylabel("RPM")
    ax.set_title("실시간 모터 RPM")
    ax.legend(loc="upper left")

    def update(frame):
        if run_event.is_set():
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
            print(f"[플로팅] 시간: {current_time:.2f}초, RPM: {rpm_value}")
        return line,

    ani = FuncAnimation(fig, update, interval=1000, blit=False)
    plt.show()
    run_event.set()


if __name__ == "__main__":
    motor = MotorController()

    if motor.connect():
        print("[메인] MODBUS-RTU 연결 성공!")

        run_event = threading.Event()
        run_event.set()
        direction_lock = threading.Lock()
        current_direction = [0]
        input_queue = Queue()

        motor_thread = threading.Thread(
            target=motor_control, args=(motor, run_event, direction_lock, current_direction, input_queue)
        )
        input_thread = threading.Thread(
            target=user_input_handler, args=(motor, run_event, input_queue)
        )

        motor_thread.start()
        input_thread.start()

        try:
            plot_rpm(motor, run_event, run_time=20)
        except KeyboardInterrupt:
            print("[메인] 사용자에 의해 중단되었습니다.")
            run_event.clear()

        motor_thread.join()
        input_thread.join()
        motor.close()
        print("[메인] MODBUS-RTU 연결 종료")
    else:
        print("[메인] MODBUS-RTU 연결 실패")
