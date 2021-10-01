import struct


class FlvChecker:
    def __init__(self, src_path, dst_path):
        self.src_path = src_path
        self.dst_path = dst_path
        self.last_timestamp_read = {b'\x08': -1, b'\x09': -1}
        self.last_timestamp_write = {b'\x08': -1, b'\x09': -1}

    def check(self):
        with self.src_path.open('rb') as src:
            with self.dst_path.open('wb+') as dst:
                head = src.read(9)
                dst.write(head)
                self.check_tag(src, dst)

        with self.dst_path.open('rb+') as dst:
            self.change_duration(dst)

    def check_tag(self, src, dst):
        current_length = 9

        while True:
            tag_size = src.read(4)  # 读取前一个tag size
            dst.write(tag_size)

            lats_valid_length = current_length  # 记录当前新文件位置，若下一tag无效，则需要回退
            current_length = dst.tell()

            tag_type = src.read(1)  # 读取tag类型
            if tag_type == b'\x08' or tag_type == b'\x09':  # 8/9 audio/video
                dst.write(tag_type)

                size_data = src.read(3)
                dst.write(size_data)
                data_size = int.from_bytes(
                    size_data, byteorder='big', signed=False)

                time_data = src.read(3)  # 时间戳 3 + 1
                time_data_ex = src.read(1)
                timestamp = int.from_bytes(
                    time_data, byteorder='big', signed=False)
                timestamp |= (int.from_bytes(
                    time_data_ex, byteorder='big', signed=False) << 24)
                self.deal_time_stamp(dst, timestamp, tag_type)

                data = src.read(3 + data_size)  # 数据
                dst.write(data)
            elif tag_type == b'\x12':  # scripts
                # 如果是scripts脚本，默认为第一个tag，此时将前一个tag Size 置零
                dst.seek(dst.tell() - 4)
                dst.write(b'\x00\x00\x00\x00')
                dst.write(tag_type)

                size_data = src.read(3)
                dst.write(size_data)
                data_size = int.from_bytes(
                    size_data, byteorder='big', signed=False)

                src.read(4)
                dst.write(b'\x00\x00\x00\x00')  # 时间戳 0

                data = src.read(3 + data_size)  # 数据
                dst.write(data)
            else:
                dst.truncate(lats_valid_length)
                break

    def deal_time_stamp(self, dst, timestamp, tag_type):
        if self.last_timestamp_read[tag_type] == -1:  # 如果是首帧
            self.last_timestamp_write[tag_type] = 0
        elif timestamp >= self.last_timestamp_read[tag_type]:  # 如果时序正常
            # 间隔十分巨大(1s)，那么重新开始即可
            if timestamp > self.last_timestamp_read[tag_type] + 1000:
                self.last_timestamp_write[tag_type] += 10
            else:
                self.last_timestamp_write[tag_type] = timestamp - \
                    self.last_timestamp_read[tag_type] + \
                    self.last_timestamp_write[tag_type]
        else:  # 如果出现倒序时间戳
            # 如果间隔不大，那么如实反馈
            if self.last_timestamp_read[tag_type] - timestamp < 5 * 1000:
                tmp = timestamp - \
                    self.last_timestamp_read[tag_type] + \
                    self.last_timestamp_write[tag_type]
                if tmp < 0:
                    tmp = 1
                self.last_timestamp_write[tag_type] = tmp
            else:  # 间隔十分巨大，那么重新开始即可
                self.last_timestamp_write[tag_type] += 10
        self.last_timestamp_read[tag_type] = timestamp

        # 低于0xffffff部分
        low_current_time = self.last_timestamp_write[tag_type] & 0xffffff
        dst.write(low_current_time.to_bytes(3, byteorder='big'))

        # 高于0xffffff部分
        high_current_time = self.last_timestamp_write[tag_type] >> 24
        dst.write(high_current_time.to_bytes(1, byteorder='big'))

    def change_duration(self, dst):
        duration = float(self.last_timestamp_write[b'\x08']) / 1000
        duration_header = b"\x08\x64\x75\x72\x61\x74\x69\x6f\x6e"

        data = dst.read(1024 * 1024)
        pointer = 0
        find_header = False
        for i in range(len(data)):
            if data[i] == duration_header[pointer]:
                pointer += 1
                if pointer == len(duration_header):  # 如果完全包含durationHeader头部，则可以返回
                    dst.seek(i + 1)
                    dst.write(b"\x00")
                    dst.write(struct.pack('>d', duration))
                    find_header = True
                    break
            else:
                pointer = 0
        if not find_header:
            pass
