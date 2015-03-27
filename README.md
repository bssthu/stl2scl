# stl2scl
Convert Siemens' STL code to SCL

将西门子Step7的STL代码转换为SCL代码。

只能转换由编译器生成的STL代码。（没有优化功能的）

目前进度：
- 转换为类似SCL的伪代码
- 支持IF结构和简单的ELSE

### Usage

```bash
python stl2scl.py -i in.stl -o out.scl
```

参数：
- -i, --input: 输入的 STL 文件，默认为 in.txt
- -o, --output: 输出的 SCL 文件，默认为 out.scl
- --keep-stl: 将 STL 代码保留并注释
- --show-label: 显示不再需要的 label

### License
GPLv3
