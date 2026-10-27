#!/usr/bin/env python3
"""兼容提示：公开PDF副本准备已停用，统一按私有附件工作流维护。"""
import argparse


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    print('公开PDF发布已停用，不生成发布资产或URL。')
    print('原文须保留原字节；中文PDF保留权利声明，按文档/工具/中文PDF发布.md私有备份。')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
