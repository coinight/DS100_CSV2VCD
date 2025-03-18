import csv
import sys
from datetime import datetime

def csv_to_vcd(csv_filename, vcd_filename, Tol=0.8):
    # 读取CSV文件
    with open(csv_filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        param_line = next(reader)
        parts = []
        parts.append(param_line[0].split("(")[1].split(")")[0].upper())
        parts.append(param_line[1].split("(")[1].split(")")[0].upper())
        parts.append(param_line[2].split(":")[1].strip())
        
        cha_factor = 0.001 if parts[0] == 'MV' else 1.0 if parts[0] == 'V' else None
        chb_factor = 0.001 if parts[1] == 'MV' else 1.0 if parts[1] == 'V' else None
        # 解析采样率
        sampling_rate = int(parts[2])
        time_step_ns = int(1e9 / sampling_rate)
        
        # 读取数据行
        data_rows = list(reader)
    
    # 创建VCD文件
    with open(vcd_filename, 'w') as vcd:
        # 写入头信息
        vcd.write("$date\n")
        vcd.write(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        vcd.write("$end\n")
        vcd.write("$version\n")
        vcd.write("   CSV to VCD Converter\n")
        vcd.write("$end\n")
        vcd.write("$timescale 1ns $end\n")
        vcd.write("$scope module logic $end\n")
        vcd.write("$var wire 1 a CHA $end\n")
        vcd.write("$var wire 1 b CHB $end\n")
        vcd.write("$upscope $end\n")
        vcd.write("$enddefinitions $end\n")
        
        # 处理数据行
        prev_cha, prev_chb = None, None
        for index, row in enumerate(data_rows):
            if len(row) < 2:
                continue
            
            try:
                cha_val = float(row[0].strip()) * cha_factor
                chb_val = float(row[1].strip()) * chb_factor
            except:
                continue  # 忽略无效行
            
            cha_logic = 1 if cha_val >= Tol else 0
            chb_logic = 1 if chb_val >= Tol else 0
            current_time = index * time_step_ns
            
            if index == 0:
                vcd.write(f"#0\n{cha_logic}a\n{chb_logic}b\n")
                prev_cha, prev_chb = cha_logic, chb_logic
            else:
                changes = []
                if cha_logic != prev_cha:
                    changes.append(f"{cha_logic}a")
                    prev_cha = cha_logic
                if chb_logic != prev_chb:
                    changes.append(f"{chb_logic}b")
                    prev_chb = chb_logic
                if changes:
                    vcd.write(f"#{current_time}\n")
                    vcd.write("\n".join(changes) + "\n")

# 使用示例
# csv_to_vcd('000.csv', 'output.vcd')
def ErrorPrint(errorCode = ""):
    print(errorCode)
    print("Usage: CSV2VCD <input.csv> [output.vcd] [Threshold Default=0.8]")
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        ErrorPrint("Too Less Input Paramater")
    input_file = sys.argv[1]
    if(input_file.split(".")[1].lower() != "csv"):
        ErrorPrint("Input file is NOT end with .csv")

    print("Input File:"+input_file)

    output_file = input_file.split(".")[0]+".vcd"
    if len(sys.argv) == 3:
        output_file = sys.argv[2]
    print("Output File:"+output_file)
    try:
        tol = float(sys.argv[3]) if len(sys.argv) > 3 else 0.8
    except:
        ErrorPrint("Threshold Value Error"+str(sys.argv[3]))
    try:
        csv_to_vcd(input_file, output_file, tol)
        print(f"Conversion successful: {output_file}")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(2)