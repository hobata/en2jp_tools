#!/bin/sh -x
date
cd foo.d

echo num of pages:
pdftk upload.pdf dump_data | grep NumberOfPages | cut -d ' ' -f 2

pdftoppm -png -f 1 -l 10 upload.pdf page

rm -f ../ocr-doc.txt
for var in 1 2 3 4 5 6 7 8 9
do
  tesseract "page-0${var}.png" outfile -l eng
  echo "page $var" >> ../ocr-doc.txt
  python ../ocr7.py outfile.txt >> ../ocr-doc.txt
  rm -f outfile.txt
done
  tesseract "page-10.png" outfile -l eng
  echo "page 10" >> ../ocr-doc.txt
  python ../ocr7.py outfile.txt >> ../ocr-doc.txt
  rm -f outfile.txt
cd ..
date

# memo
# find "." -type f -name "*.tif" | sed 's/\.tif$//' | xargs -P8 -n1 -I% tesseract %.tif % -l eng+jpn

