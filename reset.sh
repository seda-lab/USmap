#!/bin/bash
find . |grep graph | xargs rm -f
find . |grep .json | xargs rm -f
find . |grep .txt | xargs rm -f
find . |grep .png | xargs rm -f
find . |grep .out | xargs rm -f
