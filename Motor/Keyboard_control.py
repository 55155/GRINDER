from pymodbus.client import ModbusSerialClient
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import threading
from collections import deque

port = 
class MotorController:
    def __init__(self, port="/dev/ttyUSB0", baudrate=115200, device_id=100):
        """
        모터 컨트롤러 초기화
        :param port: USB 포트 경로 (예: /dev/ttyUSB0)
        :param baudrate: 통신 속도 (기본값: 115200)
        :param device_id: Device ID
        """
        self.client = ModbusSerialClient(
            port=port,
            baudrate=baudrate,
            bytesize=8,
            parity="N",
            stopbits=1,
            timeout=1
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
                response = self.client.read_holding_registers(address=address, count=count, slave=self.device_id)
            if response and not response.isError():
                return response.registers
            else:
                print(f"[Error] Failed to read register at {hex(address)}")
                return None
        except Exception as e:
            print(f"[Exception] Exception while reading register: {e}")
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
                response = self.client.write_register(address=address, value=value, slave=self.device_id)
            if response and not response.isError():
                return True
            else:
                print(f"[Error] Failed to write register at {hex(address)}")
                return False
        except Exception as e:
            print(f"[Exception] Exception while writing register: {e}")
            return False

    # 속도 설정
    def set_speed(self, speed = 100):
        if 0 <= speed <= 100: # 
            return self.write_register(0x0001, speed)
        else:
            print("[Error] Invalid speed value. Must be 0-1000 or >=1001")
            return False

    # CW/CCW 설정
    def set_cw_ccw(self, direction):
        if direction in [0, 1]:
            return self.write_register(0x0002, direction)
        else:
            print("[Error] Invalid direction. Must be 0 (CW) or 1 (CCW)")
            return False

    # 모터 시작/정지 설정
    def set_enable(self, enable):
        if enable in [0, 1]:
            return self.write_register(0x0003, enable)
        else:
            print("[Error] Invalid enable value. Must be 0 (Stop) or 1 (Start)")
            return False

    # 브레이크 설정
    def set_brake(self, brake):
        if brake in [0, 1]:
            return self.write_register(0x0004, brake)
        else:
            print("[Error] Invalid brake value. Must be 0 (OFF) or 1 (ON)")
            return False

    # 현재 속도 읽기
    def get_current_speed(self):
        return self.read_register(0x0007)

    # 현재 CW/CCW 값 읽기
    def get_current_cw_ccw(self):
        return self.read_register(0x0008)

    # 현재 모터 상태 읽기
    def get_motor_fault(self):
        return self.read_register(0x0017)

    # 현재 전류 읽기
    def get_current(self):
        return self.read_register(0x000B)  # Assuming 0x000B is current

    # 현재 RPM 읽기
    def get_current_RPM(self):
        return self.read_register(0x0015)


def user_input_handler(motor, run_event):
    """
    사용자로부터 속도 입력을 받는 함수.
    :param motor: MotorController 인스턴스
    :param run_event: 종료 이벤트
    """
    while not run_event.is_set():
        try:
            user_speed = input("[입력] 속도를 입력하세요 (0-100): ")
            if not user_speed.isdigit():
                print("[오류] 숫자를 입력하세요.")
                continue
            user_speed = int(user_speed)
            if 0 <= user_speed <= 100:
                motor.set_speed(user_speed)
                print(f"[설정] 속도가 {user_speed}로 설정되었습니다.")
            else:
                print("[오류] 속도는 0에서 100 사이여야 합니다.")
        except KeyboardInterrupt:
            print("[입력] 사용자 입력 중단")
            run_event.set()
            break


def motor_control(motor, run_event, direction_lock, current_direction, max_reversals=10): # 변속 최대 10번으로 제한
    """
    모터를 설정하고 모니터링하며 RPM이 0일 때 방향을 전환하는 함수.
    """
    reversal_count = 0

    while not run_event.is_set() and reversal_count < max_reversals:
        print("[제어] 모터 시작 준비")
        if motor.set_brake(0):
            print("[제어] 브레이크 해제 완료")
        else:
            print("[제어] 브레이크 해제 실패")
        time.sleep(0.5)

        with direction_lock:
            direction = current_direction[0]
        if motor.set_cw_ccw(direction):
            print(f"[제어] 방향이 {'CW' if direction == 0 else 'CCW'}로 설정되었습니다.")
        else:
            print("[제어] 방향 설정 실패")
        time.sleep(0.5)

        if motor.set_enable(1):
            print("[제어] 모터가 시작되었습니다.")
        else:
            print("[제어] 모터 시작 실패")

        try:
            while not run_event.is_set():
                current_rpm = motor.get_current_RPM()
                if current_rpm:
                    rpm_value = current_rpm[0]
                    print(f"[제어] 현재 RPM: {rpm_value}")
                    if rpm_value == 0:
                        print("[제어] RPM이 0입니다. 방향을 반전합니다.")
                        if motor.set_enable(0):
                            print("[제어] 모터가 정지되었습니다.")
                        else:
                            print("[제어] 모터 정지 실패")
                        time.sleep(0.5)

                        with direction_lock:
                            new_direction = 1 - current_direction[0]
                            current_direction[0] = new_direction
                            print(f"[제어] 방향이 {'CW' if new_direction == 0 else 'CCW'}로 반전되었습니다.")
                        if motor.set_enable(1):
                            print("[제어] 모터가 다시 시작되었습니다.")
                        else:
                            print("[제어] 모터 다시 시작 실패")
                        reversal_count += 1
                        break
                time.sleep(1) # time.sleep Test 환경시에만 ON
        except Exception as e:
            print(f"[제어] 모터 제어 중 예외 발생: {e}")
        
        if reversal_count >= max_reversals:
            print("[제어] 최대 반전 횟수에 도달했습니다.")
            break


def plot_rpm(motor, run_event, run_time=20):
    """
    실시간 RPM 플로팅.
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
            ax.relim()
            ax.autoscale_view()
            line.set_data(x_data, y_data)
            print(f"[플로팅] 시간: {current_time:.2f}초, RPM: {rpm_value}")
        return line,

    ani = FuncAnimation(fig, update, interval=1000, blit=False)
    plt.show()
    run_event.set()

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="모터 제어 프로그램 (포트 및 속도 설정).")
    parser.add_argument(
        "--ports", nargs="*", default=["/dev/ttyUSB0"], help="모터 제어 포트 목록 (기본값: /dev/ttyUSB0)"
    )
   
    parser.add_argument(
        "--duration", type=int, default=20, help="프로그램 실행 시간 (초, 기본값: 10초)"
    )
    args = parser.parse_args()
    # command 라인에서 정의할 수 있음, 만약 포트 변경을 원한다면, 
    # python Keyboard.py COM10
    motor = MotorController(port=args.ports)  # 실제 포트로 변경

    if motor.connect():
        print("[메인] MODBUS-RTU 연결 성공!")

        run_event = threading.Event()
        direction_lock = threading.Lock()
        current_direction = [0]
        
        # 멀티 스레드
        # PLOT 이 메인 스레드, motor와 input이 작업 스레드(worked thread)
        motor_thread = threading.Thread(target=motor_control, args=(motor, run_event, direction_lock, current_direction))
        input_thread = threading.Thread(target=user_input_handler, args=(motor, run_event))

        motor_thread.start()
        input_thread.start()

        try:
            plot_rpm(motor, run_event, run_time=20)
        except KeyboardInterrupt:
            print("[메인] 사용자에 의해 중단되었습니다.")
            run_event.set()

        motor_thread.join()
        input_thread.join()
        motor.close()
        print("[메인] MODBUS-RTU 연결 종료")
    else:
        print("[메인] MODBUS-RTU 연결 실패")
