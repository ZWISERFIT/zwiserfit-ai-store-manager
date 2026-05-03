#!/usr/bin/env python3
"""
设备心跳 & GET_LOG_DATA 模拟测试脚本
模拟可见光终端设备向 Flask 中间件发送协议请求
"""
import json
import hashlib
import requests

BASE_URL = "http://127.0.0.1:5000"
DEVICE_SECRET = "default_secret_key_change_me"


def calc_token(dev_id: str) -> str:
    return hashlib.md5((dev_id + DEVICE_SECRET).encode()).hexdigest().upper()


def send_request(request_code: str, body: dict = None, extra_headers: dict = None):
    """发送模拟设备请求"""
    dev_id = "TEST-DEVICE-001"
    dev_model = "Y80X"
    token = calc_token(dev_id)

    headers = {
        "request_code": request_code,
        "dev_id": dev_id,
        "dev_model": dev_model,
        "token": token,
        "Content-Type": "application/octet-stream",
    }
    if extra_headers:
        headers.update(extra_headers)

    resp = requests.post(BASE_URL, json=body or {}, headers=headers)

    print(f"── 请求: {request_code} ──")
    print(f"  请求头: request_code={request_code}, dev_id={dev_id}, token={token[:8]}...")
    print(f"  请求体: {body}")
    print(f"  HTTP 状态码: {resp.status_code}")
    print(f"  响应头: response_code={resp.headers.get('response_code', 'N/A')}, "
          f"trans_id={resp.headers.get('trans_id', 'N/A')}, "
          f"cmd_code={resp.headers.get('cmd_code', 'N/A')}")
    if resp.text:
        try:
            print(f"  响应体 (JSON): {json.dumps(json.loads(resp.text), indent=2, ensure_ascii=False)}")
        except Exception:
            print(f"  响应体: {resp.text}")
    else:
        print(f"  响应体: (空)")
    print()
    return resp


def test_heartbeat():
    """测试设备心跳 → ERROR_NO_CMD"""
    print("=" * 60)
    print("测试 1: 设备心跳 (receive_cmd)")
    print("预期: 无指令时返回 ERROR_NO_CMD")
    print("=" * 60)
    resp = send_request("receive_cmd", {"time": "202604291200"})


def test_get_log_data_flow():
    """测试触发 GET_LOG_DATA → 设备心跳获取 → 回传结果"""
    print("=" * 60)
    print("测试 2: 管理接口触发 GET_LOG_DATA 下发")
    print("=" * 60)

    # 2a: 管理接口触发 GET_LOG_DATA
    resp = requests.post(f"{BASE_URL}/admin/trigger_get_log", json={
        "dev_id": "TEST-DEVICE-001",
        "begin_time": "20250422",
        "end_time": "20260429",
    })
    print(f"管理接口响应: {resp.json()}")
    print()

    # 2b: 设备心跳 → 应收到 GET_LOG_DATA 指令
    resp1 = send_request("receive_cmd", {"time": "202604291201"})

    # 2c: 设备回传执行结果 (模拟打卡数据)
    mock_log_data = {
        "packageId": 0,
        "allLogCount": 3,
        "logsCount": 3,
        "logs": [
            {
                "userId": "1001",
                "time": "20260429083000",
                "verifyMode": "Card+Face",
                "ioMode": 1,
                "inOut": "In",
                "doorMode": "hand_open",
                "temperature": 36.5,
                "logPhoto": ""
            },
            {
                "userId": "1002",
                "time": "20260429090000",
                "verifyMode": "Face",
                "ioMode": 1,
                "inOut": "In",
                "doorMode": "hand_open",
                "temperature": 36.7,
                "logPhoto": _gen_test_photo_b64()
            },
            {
                "userId": "1001",
                "time": "20260429180000",
                "verifyMode": "Face",
                "ioMode": 0,
                "inOut": "Out",
                "doorMode": "hand_open",
                "temperature": 36.3,
                "logPhoto": ""
            }
        ]
    }

    send_request(
        "send_cmd_result",
        body=mock_log_data,
        extra_headers={
            "trans_id": resp1.headers.get("trans_id", "100"),
            "cmd_return_code": "OK",
        }
    )


def _gen_test_photo_b64() -> str:
    """生成一个简单的纯色 1x1 像素 JPEG 作为测试照片的 Base64"""
    # 这是一个最小的有效 JPEG 图片
    min_jpeg_hex = (
        "ffd8ffe000104a46494600010100000100010000ffdb004300080606070605080707070909080a0c"
        "140d0c0b0b0c1912130f141d1a1f1e1d1a1c1c20242e2720222c231c1c2837292c30313434341f27"
        "3f38363c3728333432ffdb0043010909090c0b0c180d0d1832211c21323232323232323232323232"
        "32323232323232323232323232323232323232323232323232323232323232323232323232ffc00011"
        "080001000103012200021101031101ffc4001f00000105010101010101000000000000000001020304"
        "05060708090a0bffc400b5100002010303020403050504040000017d010203000411051221314106"
        "13516107311422328191a10842b1c1152352d1f02433627282090a161718191a25262728292a343536"
        "3738393a434445464748494a535455565758595a636465666768696a737475767778797a8384858687"
        "88898a92939495969798999aa2a3a4a5a6a7a8a9aab2b3b4b5b6b7b8b9bac2c3c4c5c6c7c8c9cad2"
        "d3d4d5d6d7d8d9dae1e2e3e4e5e6e7e8e9eaf1f2f3f4f5f6f7f8f9faffc4001f01000301010101"
        "010101010000000000000102030405060708090a0bffc400b511000201020404030407050404000102"
        "77000102031104052131061241510761711322328108144291a1b1c109233352f0156272d10a162434"
        "e125f11718191a262728292a35363738393a434445464748494a535455565758595a63646566676869"
        "6a737475767778797a82838485868788898a92939495969798999aa2a3a4a5a6a7a8a9aab2b3b4b5b6"
        "b7b8b9bac2c3c4c5c6c7c8c9cad2d3d4d5d6d7d8d9dae2e3e4e5e6e7e8e9eaf1f2f3f4f5f6f7f8"
        "f9faffda000c03010002110311003f00f9fe8a28a0028a28a0028a28a0028a28a0028a28a0028a28a"
        "0028a28a0028a28a0028a28a0028a28a0028a28a0028a28a0028a28a0028a28a0028a28a0028a28a"
        "0028a28a0028a28a0028a28a0028a28a0028a28a00ffd9"
    )
    return bytes.fromhex(min_jpeg_hex).hex()


def test_realtime_push():
    """测试实时打卡推送"""
    print("=" * 60)
    print("测试 3: 实时打卡推送 (realtime_glog)")
    print("=" * 60)
    send_request("realtime_glog", {
        "userId": "1003",
        "time": "20260429121500",
        "verifyMode": "Face",
        "ioMode": 1,
        "inOut": "In",
        "doorMode": "hand_open",
        "temperature": 36.6,
        "logPhoto": ""
    })


def test_admin_status():
    """测试管理接口"""
    print("=" * 60)
    print("测试 4: 管理接口 - 服务器状态")
    print("=" * 60)
    resp = requests.get(f"{BASE_URL}/admin/status")
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    print()

    print("测试 5: 管理接口 - 查询打卡记录")
    resp = requests.get(f"{BASE_URL}/admin/logs?limit=10")
    result = resp.json()
    print(f"共 {result['total']} 条记录:")
    for r in result["records"]:
        print(f"  user={r['user_id']}, time={r['punch_time']}, "
              f"verify={r['verify_mode']}, photo={r['photo_path'] or 'N/A'}")


if __name__ == "__main__":
    import sys

    test_heartbeat()
    test_get_log_data_flow()
    test_realtime_push()
    test_admin_status()

    print("=" * 60)
    print("✅ 所有测试完成！")
